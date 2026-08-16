"""
JLT Inside-Sales Configurator - rough first-draft prototype.

Screens, built against the single JLT VMT price list ingested in
ingest/parse_vmt.py:

  /technical  - technical reviewer checkbox-approves which options are valid
  /sales      - rep picks a platform + approved options, saves/locks/prints/
                copies quotes tied to a manually-entered Opportunity ID
  /purchasing - all 4 price tiers, editable blanks, and an action-item report
                of what sales has quoted that still needs purchasing's input

Data lives in plain JSON files under data/ - no database yet, matching the
project's "start spreadsheet-based" approach. Cost and Current Cost are
purchasing-internal only and are never included in anything a rep or
customer sees (Sales screen, print view, Excel export).

Quote ID/lock rules (first draft - flag if this isn't quite right):
  - A quote gets its Opportunity-Quote# the first time it's saved. Rev starts at 0.
  - Locking (the Lock/Unlock toggle, or automatically on Print/Upload) "fixes"
    the quote - it can't be edited again until unlocked.
  - Editing and re-saving a quote that has ever been locked bumps Rev by 1.
  - Copy clones the configuration onto a new Opportunity ID, with a fresh
    Quote# and Rev back at 0.
"""

import csv
import io
import json
import secrets
import sys
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, send_file, session, url_for
import openpyxl
from openpyxl.styles import Font

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR / "ingest"))
import parse_vmt        # noqa: E402
import parse_winmate     # noqa: E402
import parse_getac       # noqa: E402
import parse_cipherlab   # noqa: E402

# Brand -> parser, so Technical's upload form can route each vendor's
# spreadsheet to the parser that actually understands its layout instead of
# always assuming JLT's. Every entry here is a manufacturer's own official
# catalog (see is_selectable()) - third-party add-on vendors (RAM Mounts,
# Gamber-Johnson, etc.) aren't in this registry yet; that's a separate,
# not-yet-built ingestion path that will need requires_review=True instead.
PARSERS = {
    "JLT": parse_vmt.parse_workbook,
    "Winmate": parse_winmate.parse_workbook,
    "Getac": parse_getac.parse_workbook,
    "CipherLab": parse_cipherlab.parse_workbook,
}

app = Flask(__name__)

DATA_DIR = BASE_DIR / "data"
PARTS_FILE = DATA_DIR / "parts_vmt_q1_2026.json"
APPROVALS_FILE = DATA_DIR / "approvals.json"
QUOTES_FILE = DATA_DIR / "quotes.json"
CUSTOMERS_FILE = DATA_DIR / "customers.json"
SALES_REPS_FILE = DATA_DIR / "sales_reps.json"
SITE_ACCESS_FILE = DATA_DIR / "site_access.json"
REPORTS_DIR = DATA_DIR / "reports"

# --------------------------------------------------------------- site access
# A single shared PIN gating every page/API on the whole app - not per-user,
# just a soft "don't let a random person who finds the tunnel link poke
# around" gate. Same "not real security" caveat as the sales-rep codes: a
# short PIN with no lockout. Lives in a gitignored file (never committed -
# this repo is PUBLIC on GitHub) that's auto-created with a fresh random PIN
# and session secret key the first time the app runs.

def load_or_create_site_access():
    if SITE_ACCESS_FILE.exists():
        return json.loads(SITE_ACCESS_FILE.read_text(encoding="utf-8"))
    data = {
        "pin": "".join(secrets.choice("0123456789") for _ in range(4)),
        "secret_key": secrets.token_hex(32),
    }
    SITE_ACCESS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def save_site_access(data):
    SITE_ACCESS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


_site_access = load_or_create_site_access()
app.secret_key = _site_access["secret_key"]
app.permanent_session_lifetime = timedelta(days=7)


@app.before_request
def require_site_pin():
    if request.endpoint in ("login", "static"):
        return
    if not session.get("authenticated"):
        return redirect(url_for("login", next=request.path))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    next_url = request.values.get("next") or url_for("sales")
    if request.method == "POST":
        entered = request.form.get("pin", "").strip()
        current = load_or_create_site_access()["pin"]
        if entered and entered == current:
            session.permanent = True
            session["authenticated"] = True
            return redirect(request.form.get("next") or url_for("sales"))
        error = "Incorrect PIN."
    return render_template("login.html", error=error, next=next_url)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

CATEGORY_ORDER = [
    "Base Unit:",
    "Processor Options",
    "RAM Memory Options:",
    "Storage Drive Options:",
    "Display options:",
    "Internal Options:",
    "Add On Options:",
    "IP Rating Options:",
    "Power Cable Options:",
    "Internal Wireless",
    "Operating System:",
]

PRICE_FIELDS = ["Floor Price", "MSRP", "Cost", "Current Cost"]

# Fixed-SKU brands (Getac, CipherLab - see ingest/parse_getac.py and
# ingest/parse_cipherlab.py) don't decompose into real per-category options,
# so there's nothing for Search by Requirements to match against for them
# under normal category/description matching. Their CPU/OS/RAM info lives on
# the Base Unit row's `attributes` dict instead - this maps a searchable
# category to the attribute key that can satisfy it as a fallback.
ATTRIBUTE_CATEGORY_MAP = {
    "Processor Options": "cpu",
    "Operating System:": "os",
    "RAM Memory Options:": "ram",
}
CUSTOMER_FACING_PRICE_FIELDS = ["Floor Price", "MSRP"]  # Cost/Current Cost never leave Purchasing

# Fixed roster so the Brand dropdown always shows every vendor JLT resells,
# not just whichever ones happen to have data today. All 4 are ingested and
# auto-approved as of 2026-08-16 (see PARSERS above and each brand's
# requires_review=False) - this list existing independently of ingestion
# status just means a brand added here before its parser/data exist would
# show an empty state instead of being missing from the dropdown entirely.
BRANDS = ["JLT", "Winmate", "Getac", "CipherLab"]


def category_sort_key(category):
    normalized = category.strip().rstrip(":")
    for i, c in enumerate(CATEGORY_ORDER):
        if c.strip().rstrip(":") == normalized:
            return i
    return len(CATEGORY_ORDER)


def money_value(v):
    if v in (None, ""):
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().upper()
    if s in ("INCL", "NC"):
        return 0.0
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return 0.0


# ---------------------------------------------------------------- parts data

def load_parts():
    return json.loads(PARTS_FILE.read_text(encoding="utf-8"))


def save_parts(parts):
    PARTS_FILE.write_text(json.dumps(parts, indent=2), encoding="utf-8")


def part_key(p):
    return (p["brand"], p["platform"], p["category"], p["code"])


def find_part(parts, brand, platform, category, code):
    for p in parts:
        if p["brand"] == brand and p["platform"] == platform and p["category"] == category and p["code"] == code:
            return p
    return None


def is_selectable(p, approvals):
    """A part is usable on Sales if it's from a manufacturer's own official
    catalog (requires_review=False - JLT/Winmate/Getac/CipherLab's own
    published price books today) or has been explicitly Technical-approved.
    Missing the field entirely defaults to requiring review (safe default -
    nothing slips through unreviewed by accident). Third-party add-ons (RAM
    Mounts, Gamber-Johnson, etc. - not built yet) will always need the
    explicit-approval path, since a mount vendor's own catalog doesn't
    self-certify compatibility with a specific host platform the way an
    OEM's own spec sheet does."""
    if not p.get("requires_review", True):
        return True
    return part_key(p) in approvals


# ------------------------------------------------------------------ approvals

def load_approvals():
    if not APPROVALS_FILE.exists():
        return set()
    raw = json.loads(APPROVALS_FILE.read_text(encoding="utf-8"))
    return {tuple(x) for x in raw}


def save_approvals(approvals):
    APPROVALS_FILE.write_text(
        json.dumps(sorted(list(t) for t in approvals), indent=2), encoding="utf-8"
    )


# ---------------------------------------------------------------- customers
# A local stand-in for a real CRM customer list until HubSpot is connected.
# Just names for now - enough to look up / create / attach to a quote.

def load_customers():
    if not CUSTOMERS_FILE.exists():
        return []
    return json.loads(CUSTOMERS_FILE.read_text(encoding="utf-8"))


def save_customers(customers):
    CUSTOMERS_FILE.write_text(json.dumps(customers, indent=2), encoding="utf-8")


# --------------------------------------------------------------- sales reps
# Lightweight rep identification for quote attribution - NOT real security.
# A 4-digit code (last 4 of cell number) is easily guessable; this exists so
# a quote records who touched it, not to gate access to anything.

def load_sales_reps():
    if not SALES_REPS_FILE.exists():
        return []
    return json.loads(SALES_REPS_FILE.read_text(encoding="utf-8"))


def save_sales_reps(reps):
    SALES_REPS_FILE.write_text(json.dumps(reps, indent=2), encoding="utf-8")


# --------------------------------------------------------------------- quotes

def load_quotes():
    if not QUOTES_FILE.exists():
        return {}
    return json.loads(QUOTES_FILE.read_text(encoding="utf-8"))


def save_quotes(quotes):
    QUOTES_FILE.write_text(json.dumps(quotes, indent=2), encoding="utf-8")


def lineage_key(opportunity_id, quote_number):
    return f"{opportunity_id}::{quote_number}"


def display_id(q):
    return f"{q['opportunity_id']}-{q['quote_number']}-{q['rev_number']}"


def next_quote_number(quotes, opportunity_id):
    nums = [q["quote_number"] for q in quotes.values() if q["opportunity_id"] == opportunity_id]
    return max(nums, default=0) + 1


def build_snapshot(parts, brand, platform, selections):
    """selections: {category: code} -> list of line items with Floor/MSRP only (never Cost)."""
    lines = []
    for category, code in selections.items():
        part = find_part(parts, brand, platform, category, code)
        if part is None:
            continue
        lines.append({
            "category": category,
            "code": code,
            "description": part.get("description"),
            "Floor Price": part.get("Floor Price"),
            "MSRP": part.get("MSRP"),
        })
    lines.sort(key=lambda l: category_sort_key(l["category"]))
    return lines


def quote_totals(lines):
    floor_total = sum(money_value(l["Floor Price"]) for l in lines)
    msrp_total = sum(money_value(l["MSRP"]) for l in lines)
    return floor_total, msrp_total


def quote_part_number(platform, lines):
    return "-".join([platform] + [l["code"] for l in lines])


def compute_quote_action_items(parts, quotes):
    """Line items in saved quotes whose Cost/Current Cost are still missing in
    the *current* parts data (not the quote's frozen snapshot) - shared by the
    Purchasing report and the Admin counter so they never drift apart."""
    action_items = []
    for q in quotes.values():
        brand = q.get("brand", "JLT")
        for line in q["selections"]:
            part = find_part(parts, brand, q["platform"], line["category"], line["code"])
            missing = [f for f in ("Cost", "Current Cost") if not part or part.get(f) in (None, "")]
            if missing:
                action_items.append({
                    "display_id": display_id(q),
                    "opportunity_id": q["opportunity_id"],
                    "locked": q["locked"],
                    "brand": brand,
                    "platform": q["platform"],
                    "category": line["category"],
                    "code": line["code"],
                    "description": line["description"],
                    "missing": ", ".join(missing),
                })
    return action_items


def compute_unreviewed_base_models(parts, approvals):
    """Platforms whose Base Unit option (the platform's base config) hasn't
    been technical-approved yet - i.e. review on that platform hasn't even
    started. Auto-approved (manufacturer-catalog) base units never need
    review in the first place, so they're excluded rather than counted as
    outstanding work."""
    unreviewed = []
    for p in parts:
        if p["category"] != "Base Unit:":
            continue
        if not p.get("requires_review", True):
            continue
        if part_key(p) not in approvals:
            unreviewed.append(p)
    unreviewed.sort(key=lambda p: (p["brand"], p["platform"]))
    return unreviewed


def compute_unlinked_customers(customers):
    """Manually-created customers with no hubspot_id yet - an action list so
    a manually-typed name doesn't quietly stay disconnected from the real
    HubSpot record once that connector exists."""
    unlinked = [c for c in customers if c.get("source") == "manual" and not c.get("hubspot_id")]
    unlinked.sort(key=lambda c: c["created_at"])
    return unlinked


# ------------------------------------------------------------- spreadsheet upload

def merge_parts(parts, new_rows, allow_new):
    """Merge parsed spreadsheet rows into the working parts list, matched by
    (brand, platform, category, code). A blank cell in the upload never
    erases a value already on file - only a non-blank incoming value
    overwrites, so a partial vendor refresh can't wipe out prices purchasing
    already filled in. allow_new=False means unmatched rows are skipped
    rather than creating a new part - used for Purchasing's pricing-only
    upload, which shouldn't be able to invent new catalog entries (that's
    Technical's job). Returns (added, updated, skipped) counts."""
    added = updated = skipped = 0
    # "requires_review" and "attributes" merge the same way as description/price:
    # a blank/missing incoming value never erases what's already on file. Every
    # brand parser sets requires_review explicitly (True/False, never blank), so
    # re-uploading an OEM catalog through Technical carries the same
    # auto-approval policy as the initial ingest, rather than silently
    # defaulting re-uploaded rows back to "needs review".
    mergeable_fields = ["description", "requires_review", "attributes"] + PRICE_FIELDS
    BLANK = (None, "", {}, [])

    for row in new_rows:
        brand = (row.get("brand") or "JLT").strip()
        platform = (row.get("platform") or "").strip()
        category = (row.get("category") or "").strip()
        code = (row.get("code") or "").strip() if row.get("code") is not None else ""
        if not (platform and category and code):
            skipped += 1
            continue

        existing = find_part(parts, brand, platform, category, code)
        if existing is None:
            if not allow_new:
                skipped += 1
                continue
            new_part = {"brand": brand, "platform": platform, "category": category, "code": code, "description": None, "requires_review": True}
            for f in PRICE_FIELDS:
                new_part[f] = None
            for f in mergeable_fields:
                if row.get(f) not in BLANK:
                    new_part[f] = row[f]
            parts.append(new_part)
            added += 1
        else:
            changed = False
            for f in mergeable_fields:
                val = row.get(f)
                if val not in BLANK and existing.get(f) != val:
                    existing[f] = val
                    changed = True
            if changed:
                updated += 1

    return added, updated, skipped


def parse_flat_price_table(file_storage):
    """Read Purchasing's flat pricing format - the same columns as its own
    'Generate Catalog Report': brand, platform, category, code, description,
    Floor Price, MSRP, Cost, Current Cost - from an uploaded .xlsx or .csv.
    A missing/blank brand column defaults to JLT (old reports predate the
    brand column)."""
    filename = (file_storage.filename or "").lower()
    rows = []

    if filename.endswith(".csv"):
        text = file_storage.read().decode("utf-8-sig")
        for r in csv.DictReader(io.StringIO(text)):
            rows.append(r)
    else:
        wb = openpyxl.load_workbook(file_storage, data_only=True)
        ws = wb.active
        header_cells = next(ws.iter_rows(min_row=1, max_row=1))
        headers = [c.value for c in header_cells]
        for values in ws.iter_rows(min_row=2, values_only=True):
            rows.append(dict(zip(headers, values)))

    out = []
    for r in rows:
        out.append({
            "brand": r.get("brand") or "JLT",
            "platform": r.get("platform"),
            "category": r.get("category"),
            "code": r.get("code"),
            "description": r.get("description"),
            "Floor Price": r.get("Floor Price"),
            "MSRP": r.get("MSRP"),
            "Cost": r.get("Cost"),
            "Current Cost": r.get("Current Cost"),
        })
    return out


# --------------------------------------------------------------------- pages

@app.route("/")
def index():
    return redirect(url_for("sales"))


@app.route("/technical", methods=["GET", "POST"])
def technical():
    upload_result = None

    if request.method == "POST":
        uploaded = request.files.get("file")
        if uploaded and uploaded.filename:
            brand = request.form.get("brand", "JLT")
            parser = PARSERS.get(brand)
            if parser is None:
                upload_result = {"error": f"No parser registered for brand {brand!r} yet."}
            else:
                try:
                    new_rows = parser(uploaded, brand=brand)
                except Exception as e:
                    upload_result = {"error": str(e)}
                else:
                    parts = load_parts()
                    added, updated, skipped = merge_parts(parts, new_rows, allow_new=True)
                    save_parts(parts)
                    upload_result = {"added": added, "updated": updated, "skipped": skipped, "total": len(new_rows), "brand": brand}
        elif "approved" in request.form or request.form.get("form") == "approvals":
            selected = request.form.getlist("approved")
            new_approvals = set()
            for raw_key in selected:
                brand, platform, category, code = raw_key.split("||", 3)
                new_approvals.add((brand, platform, category, code))
            save_approvals(new_approvals)

    parts = load_parts()
    approvals = load_approvals()

    brands = {b: {} for b in BRANDS}
    for p in parts:
        platforms = brands.setdefault(p["brand"], {})
        platforms.setdefault(p["platform"], []).append(p)
    for platforms in brands.values():
        for plist in platforms.values():
            plist.sort(key=lambda p: (category_sort_key(p["category"]), p["code"] or ""))

    brands = {
        brand: dict(sorted(brands[brand].items()))
        for brand in BRANDS
    }

    return render_template(
        "technical.html",
        brands=brands,
        all_brands=BRANDS,
        approvals=approvals,
        upload_result=upload_result,
    )


@app.route("/sales")
def sales():
    parts = load_parts()
    approvals = load_approvals()
    approved_parts = [p for p in parts if is_selectable(p, approvals)]

    # {brand: {platform: {category: [options]}}} - Brand is the first choice
    # on the page, filtering which platforms show up, same as Platform then
    # filters which category dropdowns show up.
    brands = {}
    for p in approved_parts:
        platforms = brands.setdefault(p["brand"], {})
        platforms.setdefault(p["platform"], {}).setdefault(p["category"], []).append(p)

    for platforms in brands.values():
        for cats in platforms.values():
            for plist in cats.values():
                plist.sort(key=lambda p: p["code"] or "")

    brands_with_data = sorted(brands.keys())

    return render_template(
        "sales.html",
        all_brands=BRANDS,
        brands_with_data=brands_with_data,
        brands_json=json.dumps(brands),
        category_order=CATEGORY_ORDER,
    )


@app.route("/api/search_options")
def api_search_options():
    """Distinct approved option descriptions per category, for populating the
    'Search by Requirements' dropdowns - a description (not a code) is the
    match key since the same code can mean different things on different
    platforms, but the description text is the actual spec a rep cares about.
    Optionally scoped to one brand via ?brand=."""
    brand_filter = request.args.get("brand") or None
    parts = load_parts()
    approvals = load_approvals()
    approved_parts = [p for p in parts if is_selectable(p, approvals)]

    by_category = {}
    for p in approved_parts:
        if brand_filter and p["brand"] != brand_filter:
            continue

        if p["category"] == "Base Unit:":
            # Not a selectable option itself, but a fixed-SKU brand's only
            # source of CPU/OS/RAM info - surface those as if they were
            # options in the matching pseudo-category (see
            # ATTRIBUTE_CATEGORY_MAP) so Getac/CipherLab base units show up
            # in the same requirement search as JLT/Winmate's real options.
            for category, attr_key in ATTRIBUTE_CATEGORY_MAP.items():
                val = (p.get("attributes") or {}).get(attr_key)
                if val:
                    by_category.setdefault(category, set()).add(val)
            continue

        if not p.get("description"):
            continue
        by_category.setdefault(p["category"], set()).add(p["description"])

    out = {cat: sorted(descs) for cat, descs in by_category.items()}
    return jsonify(out)


@app.route("/api/search_base_units", methods=["POST"])
def api_search_base_units():
    """Finds every (brand, platform) whose *approved* options satisfy every
    selected requirement (category -> exact description match). Requirements
    are optional and independent - a rep can fill in just Storage and OS and
    leave the rest blank, and any base unit with both stays in the results
    regardless of what else it does or doesn't offer."""
    body = request.get_json(force=True)
    brand_filter = body.get("brand") or None
    criteria = {k: v for k, v in (body.get("criteria") or {}).items() if v}

    parts = load_parts()
    approvals = load_approvals()
    approved_parts = [p for p in parts if is_selectable(p, approvals)]

    grouped = {}
    for p in approved_parts:
        grouped.setdefault((p["brand"], p["platform"]), []).append(p)

    def criterion_met(options, base_unit, category, desc):
        if any(o["category"] == category and o.get("description") == desc for o in options):
            return True
        # Fixed-SKU brands (Getac/CipherLab) have no real option row for
        # Processor/OS/RAM - fall back to the Base Unit's attributes dict.
        attr_key = ATTRIBUTE_CATEGORY_MAP.get(category)
        if attr_key and (base_unit.get("attributes") or {}).get(attr_key) == desc:
            return True
        return False

    matches = []
    for (brand, platform), options in grouped.items():
        if brand_filter and brand != brand_filter:
            continue
        base_unit = next((o for o in options if o["category"] == "Base Unit:"), None)
        if base_unit is None:
            continue
        if all(
            criterion_met(options, base_unit, category, desc)
            for category, desc in criteria.items()
        ):
            matches.append({
                "brand": brand,
                "platform": platform,
                "description": base_unit.get("description"),
                "floor_price": base_unit.get("Floor Price"),
                "msrp": base_unit.get("MSRP"),
            })

    matches.sort(key=lambda m: (m["brand"], m["platform"]))
    return jsonify(matches)


@app.route("/quote/<path:opportunity_id>/<int:quote_number>/print")
def quote_print(opportunity_id, quote_number):
    quotes = load_quotes()
    key = lineage_key(opportunity_id, quote_number)
    q = quotes.get(key)
    if q is None:
        return "Quote not found", 404

    if not q["locked"]:
        q["locked"] = True
        q["ever_locked"] = True
        q["updated_at"] = datetime.now().isoformat(timespec="seconds")
        save_quotes(quotes)

    return render_template("quote_print.html", q=q, display_id=display_id(q))


@app.route("/purchasing", methods=["GET", "POST"])
def purchasing():
    parts = load_parts()
    quotes = load_quotes()

    upload_result = None
    uploaded = request.files.get("file") if request.method == "POST" else None
    if uploaded and uploaded.filename:
        try:
            new_rows = parse_flat_price_table(uploaded)
        except Exception as e:
            upload_result = {"error": str(e)}
        else:
            added, updated, skipped = merge_parts(parts, new_rows, allow_new=False)
            save_parts(parts)
            parts = load_parts()
            upload_result = {"added": added, "updated": updated, "skipped": skipped, "total": len(new_rows)}

    if request.method == "POST" and request.form.get("action") == "save_prices":
        keys = request.form.getlist("row_key")
        for row_key in keys:
            brand, platform, category, code = row_key.split("||", 3)
            part = find_part(parts, brand, platform, category, code)
            if part is None:
                continue
            for field in PRICE_FIELDS:
                field_input_name = f"{row_key}||{field}"
                if field_input_name in request.form:
                    raw = request.form[field_input_name].strip()
                    part[field] = raw if raw != "" else None
        save_parts(parts)
        parts = load_parts()

    flagged = [
        p for p in parts
        if any(p.get(f) in (None, "") for f in PRICE_FIELDS)
    ]

    report_generated = None
    if request.method == "POST" and request.form.get("action") == "generate_catalog_report":
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_path = REPORTS_DIR / f"purchasing_catalog_report_{datetime.now():%Y%m%d_%H%M%S}.csv"
        fieldnames = ["brand", "platform", "category", "code", "description"] + PRICE_FIELDS
        with open(report_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for p in flagged:
                writer.writerow({k: p.get(k) for k in fieldnames})
        report_generated = report_path.name

    action_items = compute_quote_action_items(parts, quotes)

    quotes_report_generated = None
    if request.method == "POST" and request.form.get("action") == "generate_quotes_report":
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_path = REPORTS_DIR / f"purchasing_quotes_report_{datetime.now():%Y%m%d_%H%M%S}.csv"
        fieldnames = ["display_id", "opportunity_id", "locked", "brand", "platform", "category", "code", "description", "missing"]
        with open(report_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in action_items:
                writer.writerow(item)
        quotes_report_generated = report_path.name

    return render_template(
        "purchasing.html",
        flagged=flagged,
        total_parts=len(parts),
        report_generated=report_generated,
        price_fields=PRICE_FIELDS,
        action_items=action_items,
        quotes_report_generated=quotes_report_generated,
        total_quotes=len(quotes),
        upload_result=upload_result,
    )


@app.route("/admin", methods=["GET", "POST"])
def admin():
    parts = load_parts()
    quotes = load_quotes()
    approvals = load_approvals()

    action_items = compute_quote_action_items(parts, quotes)
    unreviewed = compute_unreviewed_base_models(parts, approvals)

    SAMPLE_TEST_CUSTOMERS = [
        "Acme Manufacturing", "Northwind Logistics", "Sunrise Distribution",
        "Blue Ridge Industrial", "Harborview Freight",
    ]
    if request.method == "POST" and request.form.get("action") == "seed_test_customers":
        customers = load_customers()
        existing_names = {c["name"] for c in customers}
        now = datetime.now().isoformat(timespec="seconds")
        for name in SAMPLE_TEST_CUSTOMERS:
            if name not in existing_names:
                customers.append({"name": name, "source": "test", "hubspot_id": None, "created_at": now})
        save_customers(customers)

    if request.method == "POST" and request.form.get("action") == "remove_test_customers":
        customers = [c for c in load_customers() if c.get("source") != "test"]
        save_customers(customers)

    customers = load_customers()
    unlinked_customers = compute_unlinked_customers(customers)
    test_customers = sorted([c for c in customers if c.get("source") == "test"], key=lambda c: c["name"])

    customer_report_generated = None
    if request.method == "POST" and request.form.get("action") == "generate_customer_report":
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_path = REPORTS_DIR / f"unlinked_customers_report_{datetime.now():%Y%m%d_%H%M%S}.csv"
        fieldnames = ["name", "source", "hubspot_id", "created_at"]
        with open(report_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for c in unlinked_customers:
                writer.writerow({k: c.get(k) for k in fieldnames})
        customer_report_generated = report_path.name

    rep_error = None
    if request.method == "POST" and request.form.get("action") == "add_rep":
        rep_name = request.form.get("rep_name", "").strip()
        rep_code = request.form.get("rep_code", "").strip()
        if not rep_name:
            rep_error = "Rep name is required."
        elif not (rep_code.isdigit() and len(rep_code) == 4):
            rep_error = "Code must be exactly 4 digits."
        else:
            reps = load_sales_reps()
            if any(r["name"] == rep_name for r in reps):
                rep_error = f'"{rep_name}" is already in the list.'
            else:
                reps.append({"name": rep_name, "code": rep_code, "created_at": datetime.now().isoformat(timespec="seconds")})
                save_sales_reps(reps)

    if request.method == "POST" and request.form.get("action") == "remove_rep":
        rep_name = request.form.get("rep_name", "").strip()
        reps = [r for r in load_sales_reps() if r["name"] != rep_name]
        save_sales_reps(reps)

    pin_error = None
    if request.method == "POST" and request.form.get("action") == "change_site_pin":
        new_pin = request.form.get("new_pin", "").strip()
        if not (new_pin.isdigit() and 4 <= len(new_pin) <= 8):
            pin_error = "PIN must be 4-8 digits."
        else:
            access = load_or_create_site_access()
            access["pin"] = new_pin
            save_site_access(access)

    all_platforms = sorted({p["platform"] for p in parts})

    return render_template(
        "admin.html",
        total_quotes=len(quotes),
        action_items_count=len(action_items),
        unreviewed=unreviewed,
        reviewed_count=len(all_platforms) - len(unreviewed),
        total_platforms=len(all_platforms),
        unlinked_customers=unlinked_customers,
        customer_report_generated=customer_report_generated,
        test_customers=test_customers,
        sales_reps=sorted(load_sales_reps(), key=lambda r: r["name"]),
        rep_error=rep_error,
        site_pin=load_or_create_site_access()["pin"],
        pin_error=pin_error,
    )


# ------------------------------------------------------------------ quote API

@app.route("/api/quotes")
def api_quotes_for_opportunity():
    opportunity_id = request.args.get("opportunity_id", "")
    quotes = load_quotes()
    matches = [q for q in quotes.values() if q["opportunity_id"] == opportunity_id]
    matches.sort(key=lambda q: (q["quote_number"], q["rev_number"]))
    return jsonify([
        {
            "display_id": display_id(q),
            "opportunity_id": q["opportunity_id"],
            "customer": q.get("customer", ""),
            "quote_number": q["quote_number"],
            "rev_number": q["rev_number"],
            "locked": q["locked"],
            "brand": q.get("brand", "JLT"),
            "platform": q["platform"],
            "part_number": q["part_number"],
            "updated_at": q["updated_at"],
        }
        for q in matches
    ])


@app.route("/api/quotes/all")
def api_quotes_all():
    """Every saved quote, for the Sales-page 'Lookup saved quote' panel -
    unlike /api/quotes this isn't filtered to one Opportunity ID."""
    quotes = load_quotes()
    out = [
        {
            "display_id": display_id(q),
            "opportunity_id": q["opportunity_id"],
            "customer": q.get("customer", ""),
            "quote_number": q["quote_number"],
            "rev_number": q["rev_number"],
            "locked": q["locked"],
            "brand": q.get("brand", "JLT"),
            "platform": q["platform"],
            "part_number": q["part_number"],
            "updated_at": q["updated_at"],
        }
        for q in quotes.values()
    ]
    out.sort(key=lambda q: q["updated_at"], reverse=True)
    return jsonify(out)


@app.route("/api/customers")
def api_customers_list():
    """Returns {name, source} per customer - the client needs `source` to
    show the right badge/Populate button. Not just the customer's name: how
    it was *found this session* (typed vs picked from the list) isn't the
    same thing as whether it's actually a real HubSpot record."""
    query = (request.args.get("q") or "").strip().lower()
    customers = load_customers()
    if query:
        customers = [c for c in customers if query in c["name"].lower()]
    out = [{"name": c["name"], "source": c.get("source", "manual")} for c in customers]
    out.sort(key=lambda c: c["name"])
    return jsonify(out)


@app.route("/api/customers", methods=["POST"])
def api_customers_create():
    """Manual Customer button: records a customer with source='manual' and no
    hubspot_id. These show up on the Admin page as pending a HubSpot link, so
    a manually-typed name doesn't silently become an orphaned opportunity
    once the real connector exists."""
    body = request.get_json(force=True)
    name = (body.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Customer name is required."}), 400
    customers = load_customers()
    if not any(c["name"] == name for c in customers):
        customers.append({
            "name": name,
            "source": "manual",
            "hubspot_id": None,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        })
        save_customers(customers)
    return jsonify({"name": name})


@app.route("/api/sales_reps")
def api_sales_reps_list():
    names = sorted(r["name"] for r in load_sales_reps())
    return jsonify(names)


@app.route("/api/sales_reps/verify", methods=["POST"])
def api_sales_reps_verify():
    body = request.get_json(force=True)
    name = (body.get("name") or "").strip()
    code = (body.get("code") or "").strip()
    reps = load_sales_reps()
    match = next((r for r in reps if r["name"] == name), None)
    if match is None:
        return jsonify({"ok": False, "error": "Unknown rep."}), 404
    if match["code"] != code:
        return jsonify({"ok": False, "error": "Code doesn't match."}), 401
    return jsonify({"ok": True, "name": name})


@app.route("/api/quotes/<path:opportunity_id>/<int:quote_number>")
def api_quote_get(opportunity_id, quote_number):
    quotes = load_quotes()
    q = quotes.get(lineage_key(opportunity_id, quote_number))
    if q is None:
        return jsonify({"error": "not found"}), 404
    out = dict(q)
    out["display_id"] = display_id(q)
    return jsonify(out)


@app.route("/api/quotes/save", methods=["POST"])
def api_quote_save():
    body = request.get_json(force=True)
    opportunity_id = (body.get("opportunity_id") or "").strip()
    if not opportunity_id:
        return jsonify({"error": "Opportunity ID is required."}), 400

    sales_rep = (body.get("sales_rep") or "").strip()
    sales_rep_code = (body.get("sales_rep_code") or "").strip()
    if not sales_rep:
        return jsonify({"error": "Select a Sales Rep first."}), 400
    rep_match = next((r for r in load_sales_reps() if r["name"] == sales_rep), None)
    if rep_match is None or rep_match["code"] != sales_rep_code:
        return jsonify({"error": "Sales rep code doesn't match. Re-enter your 4-digit code."}), 401

    customer = (body.get("customer") or "").strip()
    brand = body.get("brand") or "JLT"
    platform = body.get("platform")
    selections = body.get("selections") or {}
    quote_number = body.get("quote_number")

    parts = load_parts()
    lines = build_snapshot(parts, brand, platform, selections)
    floor_total, msrp_total = quote_totals(lines)
    part_number = quote_part_number(platform, lines)
    now = datetime.now().isoformat(timespec="seconds")

    quotes = load_quotes()

    if quote_number is not None:
        key = lineage_key(opportunity_id, quote_number)
        q = quotes.get(key)
        if q is None:
            return jsonify({"error": "Quote not found."}), 404
        if q["locked"]:
            return jsonify({"error": "This quote is locked. Unlock it before making changes."}), 400
        if q.get("ever_locked"):
            q["rev_number"] += 1
        q["customer"] = customer
        q["brand"] = brand
        q["platform"] = platform
        q["selections"] = lines
        q["floor_total"] = floor_total
        q["msrp_total"] = msrp_total
        q["part_number"] = part_number
        q["sales_rep"] = sales_rep
        q["updated_at"] = now
    else:
        quote_number = next_quote_number(quotes, opportunity_id)
        key = lineage_key(opportunity_id, quote_number)
        q = {
            "opportunity_id": opportunity_id,
            "customer": customer,
            "quote_number": quote_number,
            "rev_number": 0,
            "locked": False,
            "ever_locked": False,
            "brand": brand,
            "platform": platform,
            "selections": lines,
            "floor_total": floor_total,
            "msrp_total": msrp_total,
            "part_number": part_number,
            "created_by": sales_rep,
            "sales_rep": sales_rep,
            "created_at": now,
            "updated_at": now,
        }
        quotes[key] = q

    save_quotes(quotes)
    out = dict(q)
    out["display_id"] = display_id(q)
    return jsonify(out)


@app.route("/api/quotes/<path:opportunity_id>/<int:quote_number>/lock", methods=["POST"])
def api_quote_lock(opportunity_id, quote_number):
    body = request.get_json(force=True)
    locked = bool(body.get("locked"))

    quotes = load_quotes()
    key = lineage_key(opportunity_id, quote_number)
    q = quotes.get(key)
    if q is None:
        return jsonify({"error": "Quote not found."}), 404

    q["locked"] = locked
    if locked:
        q["ever_locked"] = True
    q["updated_at"] = datetime.now().isoformat(timespec="seconds")
    save_quotes(quotes)

    out = dict(q)
    out["display_id"] = display_id(q)
    return jsonify(out)


@app.route("/api/quotes/<path:opportunity_id>/<int:quote_number>/copy", methods=["POST"])
def api_quote_copy(opportunity_id, quote_number):
    body = request.get_json(force=True)
    new_opportunity_id = (body.get("new_opportunity_id") or "").strip()
    new_customer = (body.get("new_customer") or "").strip()
    if not new_opportunity_id:
        return jsonify({"error": "New Opportunity ID is required."}), 400

    sales_rep = (body.get("sales_rep") or "").strip()
    sales_rep_code = (body.get("sales_rep_code") or "").strip()
    if not sales_rep:
        return jsonify({"error": "Select a Sales Rep first."}), 400
    rep_match = next((r for r in load_sales_reps() if r["name"] == sales_rep), None)
    if rep_match is None or rep_match["code"] != sales_rep_code:
        return jsonify({"error": "Sales rep code doesn't match. Re-enter your 4-digit code."}), 401

    quotes = load_quotes()
    src = quotes.get(lineage_key(opportunity_id, quote_number))
    if src is None:
        return jsonify({"error": "Source quote not found."}), 404

    new_quote_number = next_quote_number(quotes, new_opportunity_id)
    now = datetime.now().isoformat(timespec="seconds")
    new_q = {
        "opportunity_id": new_opportunity_id,
        "customer": new_customer or src.get("customer", ""),
        "quote_number": new_quote_number,
        "rev_number": 0,
        "locked": False,
        "ever_locked": False,
        "brand": src.get("brand", "JLT"),
        "platform": src["platform"],
        "selections": [dict(l) for l in src["selections"]],
        "floor_total": src["floor_total"],
        "msrp_total": src["msrp_total"],
        "part_number": src["part_number"],
        "created_by": sales_rep,
        "sales_rep": sales_rep,
        "copied_from": display_id(src),
        "created_at": now,
        "updated_at": now,
    }
    quotes[lineage_key(new_opportunity_id, new_quote_number)] = new_q
    save_quotes(quotes)

    out = dict(new_q)
    out["display_id"] = display_id(new_q)
    return jsonify(out)


@app.route("/api/quotes/<path:opportunity_id>/<int:quote_number>/upload", methods=["POST"])
def api_quote_upload(opportunity_id, quote_number):
    return jsonify({
        "status": "not_connected",
        "message": "HubSpot isn't connected yet. This button is a placeholder for that future integration.",
    })


@app.route("/api/quotes/<path:opportunity_id>/<int:quote_number>/export.xlsx")
def api_quote_export(opportunity_id, quote_number):
    quotes = load_quotes()
    q = quotes.get(lineage_key(opportunity_id, quote_number))
    if q is None:
        return "Quote not found", 404

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Quote"

    bold = Font(bold=True)
    ws["A1"] = "Quote ID:"
    ws["B1"] = display_id(q)
    ws["A2"] = "Sales Rep:"
    ws["B2"] = q.get("sales_rep", "")
    ws["A3"] = "Customer:"
    ws["B3"] = q.get("customer", "")
    ws["A4"] = "Opportunity ID:"
    ws["B4"] = q["opportunity_id"]
    ws["A5"] = "Brand:"
    ws["B5"] = q.get("brand", "JLT")
    ws["A6"] = "Platform:"
    ws["B6"] = q["platform"]
    ws["A7"] = "Part Number:"
    ws["B7"] = q["part_number"]
    ws["A8"] = "Date:"
    ws["B8"] = q["updated_at"]
    for cell in ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"):
        ws[cell].font = bold

    header_row = 10
    headers = ["Category", "Code", "Description"] + CUSTOMER_FACING_PRICE_FIELDS
    for col, h in enumerate(headers, start=1):
        c = ws.cell(row=header_row, column=col, value=h)
        c.font = bold

    r = header_row + 1
    for line in q["selections"]:
        ws.cell(row=r, column=1, value=line["category"])
        ws.cell(row=r, column=2, value=line["code"])
        ws.cell(row=r, column=3, value=line["description"])
        ws.cell(row=r, column=4, value=line["Floor Price"])
        ws.cell(row=r, column=5, value=line["MSRP"])
        r += 1

    ws.cell(row=r + 1, column=3, value="Floor Total").font = bold
    ws.cell(row=r + 1, column=4, value=q["floor_total"])
    ws.cell(row=r + 2, column=3, value="MSRP Total").font = bold
    ws.cell(row=r + 2, column=4, value=q["msrp_total"])

    for col, width in zip("ABCDE", (24, 10, 50, 14, 14)):
        ws.column_dimensions[col].width = width

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    filename = f"quote_{display_id(q)}.xlsx"
    return send_file(
        buf,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
