# JLT Inside-Sales Configurator — Handoff Brief

Written 2026-08-15 for handing this project to another agent/developer. Goal: everything
needed to understand, run, extend, or fully recreate this project without access to the
conversation that built it.

## 0. Required change-log and TODO workflow — read before changing anything

`CHANGELOG.md` is the **canonical source of truth** for both completed changes and
`Pending / TODO` work. `HANDOFF.md` explains architecture and context; it must not be used
as a substitute for checking the live changelog.

Before starting work:

1. Read `AGENTS.md` for mandatory repository instructions.
2. Read `CHANGELOG.md`, especially `Pending / TODO`, before choosing or beginning work.
3. Check `main` and open pull requests so work already in progress is not duplicated.

For every repository change:

1. Add a dated `CHANGELOG.md` entry in the same branch or pull request.
2. Attribute the entry to the person or agent that made it. OpenAI Codex uses
   `**[Codex]**`; other contributors use their own clear attribution.
3. Describe the concrete code, configuration, data, documentation, or workflow affected.
4. If necessary work is identified but not completed, add it to `Pending / TODO` with its
   source, current status, and next action. This includes a pull request still awaiting
   merge into `main`.
5. When a TODO is completed, close or update it with another dated, attributed entry.
6. After the change is verified, automatically merge it into `main` without waiting for a separate merge instruction, unless the user explicitly requests a draft/unmerged branch or verification is blocked.
7. Read `main` back after the merge and confirm the expected commit and changelog entries are present.

**Standing automatic-merge instruction (added 2026-08-15 by Codex):** for this repository, a user request to update the repository authorizes Codex to merge the verified change into `main` automatically. A separate “merge it” instruction is not required. Codex must stop before merging only if the user asks to keep the work as a draft, verification fails, or an unresolved blocker requires user input.

**Current git status (updated 2026-08-15 by Codex):** the repository is committed and pushed
to GitHub. `main` is the official/default branch; active work may exist in pull-request
branches. The earlier warning that nothing had been committed is resolved. Always verify
the current GitHub branch and PR state rather than relying on the historical local state.

---

## 1. What this is and why

**Goal (from the original project brief):** replace a paper-based, error-prone process
where field sales reps hand-write system configurations and mail them in for pricing. Two
problems, one tool:
- **Sales:** let reps build a valid, correctly-priced configuration themselves.
- **Technical:** bake compatibility rules in so configs are valid *by construction*,
  cutting the repetitive technical review that currently eats headcount.

**The bigger goal:** this is not just a JLT configurator. It's meant to become a
configurator *engine* that also handles 3 other vendors JLT resells (Winmate, Getac,
CipherLab), none of which have a configurator of their own today. See §7 for how far that
part actually got.

**Long-term integration target (not built yet):** HubSpot is the front door. A sales
opportunity starts there; the configurator reads/writes back to it by deal ID. See §9 for
what currently stands in for that.

**Current status:** rough working prototype. All 4 screens (Technical, Sales, Purchasing,
Admin) are functional against real JLT pricing data. No database, no auth, no HubSpot — all
noted below.

---

## 2. Where everything lives

| What | Path |
|---|---|
| **This repo** | `C:\Users\Admin\Box\My Libraries\JLT\temp\Jeff temp\claude code\configurator\Git\` |
| **GitHub repository (main + PR branches)** | `https://github.com/jgarizona/SalesConfig.git` |
| **Source vendor spreadsheets (Box, human-edited)** | `C:\Users\Admin\Box\My Libraries\JLT\temp\Jeff temp\claude code\configurator\` (one level up from the repo) — contains `JLT VMT Q1 2026 Updated final 02192026 Release.xlsx`, `JLT Winmate Master Price Book 03062026.xlsx`, `GetacSelectMSRP_2026-01-20.xlsx`, `CipherLab Price Increase effective 4_10_2026 Product List.xlsx` |
| **Runtime data (JSON, working state)** | `Git\data\*.json` — see §6 |

Run it with:
```bash
cd "C:\Users\Admin\Box\My Libraries\JLT\temp\Jeff temp\claude code\configurator\Git"
pip install -r requirements.txt
python app.py
```
Flask dev server on `http://127.0.0.1:5000`, debug mode on (auto-reloads on file change).
**This is a dev server, not production-ready** — no WSGI server, no HTTPS, no auth beyond
the rep-code gimmick described in §8.

---

## 3. Tech stack

- **Backend:** Python 3.12, Flask. No ORM, no database — see `requirements.txt` (just
  `flask` and `openpyxl`).
- **Frontend:** server-rendered Jinja2 templates + vanilla JavaScript (no build step, no
  framework, no npm). All JS is inline `<script>` in each template.
- **Data storage:** flat JSON files under `data/`. Chosen deliberately (see brief's original
  rationale) — source data arrives as Excel, purchasing/technical reviewers already live in
  spreadsheets, and Box was the assumed eventual sync point. Migrate to a real DB only if
  this gets outgrown (concurrent multi-user editing is the likely trigger — see §10).
- **Excel I/O:** `openpyxl` for both reading vendor spreadsheets (`ingest/parse_vmt.py`) and
  writing exports (quote Excel export, Purchasing CSV/xlsx reports).

---

## 4. File structure

```
Git/
├── app.py                    # The entire Flask app — routes, data access, business logic (~1020 lines)
├── requirements.txt          # flask, openpyxl
├── CHANGELOG.md              # Dated changelog + "Pending / TODO" section — READ THIS TOO
├── HANDOFF.md                # This file
├── AGENTS.md                 # Mandatory repository instructions for AI/coding agents
├── .claude/
│   └── launch.json           # Dev-server launch config for the Claude Code browser preview tool
├── ingest/
│   └── parse_vmt.py          # Standalone script + importable module: parses JLT-format vendor
│                              # spreadsheets into normalized JSON. Also invoked live by
│                              # Technical's "Upload vendor spreadsheet" button.
├── templates/                # Jinja2 templates, one per screen + shared partials
│   ├── base.html             #   Nav bar, page shell
│   ├── technical.html        #   Technical Review screen
│   ├── sales.html            #   Sales Configurator screen (by far the largest — ~955 lines,
│                              #     most of it inline JS driving the whole quote lifecycle)
│   ├── purchasing.html       #   Purchasing Review screen
│   ├── admin.html            #   Admin Overview screen
│   └── quote_print.html      #   Standalone printable quote view (not extended from base.html)
├── static/
│   └── style.css             # All styling, hand-written, no framework (~480 lines)
└── data/                     # Runtime state — see §6 for exact schemas
    ├── parts_vmt_q1_2026.json
    ├── approvals.json
    ├── quotes.json
    ├── customers.json
    ├── sales_reps.json
    ├── site_access.json      # Site PIN + Flask session secret key - GITIGNORED, never commit (repo is public)
    └── reports/              # Generated CSV reports land here (created on demand, gitignore candidate)
```

---

## 5. The four screens

All routes live in `app.py`. Nav bar (`templates/base.html`) links all four.

### `/technical` — Technical Review
- Checkbox-approve which vendor options are valid/buildable, **grouped by Brand → Platform
  → Category**. Only checked options become selectable on Sales.
- **Upload vendor spreadsheet** form: pick a Brand, upload an `.xlsx` in the JLT multi-tab
  layout, parses via `ingest/parse_vmt.py`, merges into `parts_vmt_q1_2026.json`. New
  platforms/options land unapproved. See §9 for the "only JLT's layout is understood" caveat.
- A sticky "Save Approvals" bar (the page has ~500 checkboxes; the button used to be
  unreachable without scrolling — now always visible) and a jump-to-platform nav.

### `/sales` — Sales Configurator
The big one. Top-to-bottom:
1. **Sales Rep** dropdown + 4-digit code, verified against `sales_reps.json`. **The entire
   rest of the page is disabled until this succeeds** — see §8, this is explicitly *not*
   real security.
2. **Customer** field — always directly typeable. Typing something new flashes a green
   **Accept** button (nothing saves until clicked, or Enter). A badge next to the label
   shows "Manual — not in HubSpot" (amber) or "Existing customer" (green, currently never
   true since no customer is ever real HubSpot data yet) based on the customer record's
   actual `source` field — **not** how it was selected this session (a real bug that was
   fixed once: don't reintroduce it).
   - **Customer Lookup** button: opens a live-filtered panel using the Customer field itself
     as the filter (no separate search box).
   - **Manual Customer** button: just focuses/selects the field for typing.
3. **Opportunity ID** — free-text, manually entered (HubSpot deal ID stand-in). Exact-match,
   case-sensitive, no normalization — a typo creates a whole new opportunity silently. A
   blue "Select one →" hint badge appears once a customer is chosen but this is still empty.
   - **Populate** button (only visible when the current customer is manual, not a HubSpot
     record): fills this field with the customer name as a starting point.
   - **Lookup Saved Quote** button: searches *all* saved quotes by customer/opportunity/
     platform/quote ID, not just ones under whatever's currently typed here.
4. **Quote # / Rev #** readout boxes (auto-assigned on Save, not user-entered) + **Copy to
   New Opportunity** (opens an inline panel — new Opportunity ID + optional new Customer —
   clones the current config to a fresh quote lineage starting at Rev 0).
5. **Save / Lock / Print (PDF) / Upload / Email** action row. See §8 for the exact
   lock/rev-increment rules and which buttons require what.
6. **Brand** dropdown, **Platform** dropdown (filtered to the selected brand), **Search by
   Requirements** button (opens the modal described below).
7. Category dropdowns (Processor, RAM, Storage, Display, ports, Add-Ons, IP Rating, Power
   Cable, Wireless, OS — order fixed by `CATEGORY_ORDER` in `app.py`), live price totals,
   draft part number.
8. **Accept Configuration** button — Save is disabled until this is clicked; changing any
   option after accepting re-locks Save; the same reset happens after every successful save
   too (each save needs its own fresh Accept).
9. **Search by Requirements modal**: pick zero or more desired specs per category (optional,
   independent), optionally narrow by Brand, hit Search → every base unit whose
   **Technical-approved** options satisfy all selected criteria, radio list, Select loads
   that Brand+Platform into the main form to finish configuring and save. Matches on option
   *description text*, not code (codes aren't consistent across platforms).

### `/purchasing` — Purchasing Review
Two independent sections:
1. **Catalog pricing gaps** — every option missing any of the 4 price fields (Floor Price,
   MSRP, Cost, Current Cost), editable inline, "Save Prices" writes back to
   `parts_vmt_q1_2026.json`. "Upload pricing spreadsheet" bulk-applies a flat `.xlsx`/`.csv`
   in the same shape as "Generate Catalog Report" — **can only update existing parts, never
   create new ones** (that's Technical's job). "Generate Catalog Report" exports the gaps
   as CSV.
2. **What's been quoted to Sales — action items** — every saved quote's line items
   cross-checked against *current* pricing (not the quote's frozen snapshot), flagging
   exactly what's still missing before purchasing can sign off. Own CSV export.

Shared upload rule (`merge_parts()` in `app.py`): **a blank cell in an upload never erases a
value already on file** — only non-blank incoming values overwrite. This is what stops a
partial vendor refresh from wiping purchasing's manual price entries.

### `/admin` — Admin Overview
Stat cards + detail tables:
- Quotes created (count).
- Purchasing action items pending (same computation Purchasing uses — one source of truth).
- Platforms with base model reviewed (X / Y) + table of which ones aren't.
- Customers pending a HubSpot link (manually-created customers with no `hubspot_id`) + CSV
  report + a "Test customers" sub-section (seed/remove 5 fake customers for testing Customer
  Lookup — tagged `source:"test"` so they're excluded from the pending-link report).
- **Sales Reps** management: add (name + 4-digit code) / remove. This is where
  `sales_reps.json` gets edited.

---

## 6. Data model — exact JSON shapes

All files are in `data/`. None are schema-validated; these shapes are enforced only by
`app.py`'s code, not by anything structural. **`brand` was retrofitted onto an
already-running system** (2026-08-15) — every read path that keys on a part/approval/quote
now expects `brand` to be present; if you ever hand-edit these files or write a new ingest
path, don't forget it.

### `parts_vmt_q1_2026.json` — the catalog
List of option records (**despite the filename, this now holds all brands** — it was never
renamed after the brand retrofit; renaming it plus updating the two `PARTS_FILE` references
in `app.py` would be a reasonable cleanup):
```json
{
  "brand": "JLT",
  "platform": "1014P",
  "category": "Base Unit:",
  "code": "14P",
  "description": "Rugged Fixed Mount Computer, JLT1014P, ...",
  "Floor Price": 2660,
  "MSRP": 5320,
  "Cost": 1700,
  "Current Cost": 1669.71
}
```
`Floor Price`/`MSRP`/`Cost`/`Current Cost` are `None` when unknown, a number when known, or
occasionally the literal strings `"Incl"` / `"NC"` (included / no charge) carried straight
from the vendor spreadsheet — client and server both parse these specially (`moneyValue()`
in JS, `money_value()` in Python) treating them as 0 for totals. Currently 499 rows, all
`brand:"JLT"`.

### `approvals.json` — Technical sign-off
List of 4-element arrays: `[brand, platform, category, code]`. Presence in this list is what
makes an option selectable on Sales. Order/uniqueness not enforced beyond what
`compute_*` functions assume (treated as a set via `part_key()` matching).

### `quotes.json` — saved quotes
Dict keyed by `"{opportunity_id}::{quote_number}"` (this is `lineage_key()` in `app.py` —
**note the key does not include brand**, only opportunity_id+quote_number, so quote
numbering is scoped per-opportunity across all brands, not per-brand). Each value:
```json
{
  "opportunity_id": "CW-APMPERU",
  "customer": "Acme Corp",
  "quote_number": 1,
  "rev_number": 0,
  "locked": false,
  "ever_locked": false,
  "brand": "JLT",
  "platform": "1014P",
  "selections": [
    {"category": "Base Unit:", "code": "14P", "description": "...", "Floor Price": 2660, "MSRP": 5320}
  ],
  "floor_total": 2970.0,
  "msrp_total": 5840.0,
  "part_number": "1014P-14P-D-G-4-P-99-X-1-P-KM-255",
  "created_by": "Chad",
  "sales_rep": "Chad",
  "copied_from": "CW-APMPERU-1-0",
  "created_at": "2026-08-15T14:43:56",
  "updated_at": "2026-08-15T14:43:56"
}
```
`selections` is a **frozen snapshot** taken at save time (never Cost/Current Cost — those
never leave Purchasing). `created_by` is set once and never changes; `sales_rep` updates on
every save. `copied_from` only exists on quotes created via the Copy button. Display ID
shown everywhere is `f"{opportunity_id}-{quote_number}-{rev_number}"`.

### `customers.json` — local customer stand-in (no CRM yet)
List of:
```json
{"name": "Acme Manufacturing", "source": "test", "hubspot_id": null, "created_at": "2026-08-15T09:27:48"}
```
`source` is one of `"manual"` (typed by a rep and Accepted), `"test"` (seeded demo data via
Admin), or — not implemented — `"hubspot"` for a future real synced record. **The
Manual-badge/Populate-button UI logic on Sales treats anything that isn't `"hubspot"` as
needing the manual treatment** — so `"test"` customers behave identically to `"manual"` ones
in the UI, which is intentional.

### `sales_reps.json` — rep roster
List of:
```json
{"name": "Chad", "code": "8845", "created_at": "2026-08-15T08:54:20"}
```
Currently seeded with Chad/Glenn/Eric/Test (codes are the last 4 digits of their real cell
numbers, per the actual user's instruction — only the 4-digit codes are stored, never full
phone numbers). **This is not authentication** — see §8.

---

## 7. Multi-brand: what's built vs what's real data

`BRANDS = ["JLT", "Winmate", "Getac", "CipherLab"]` (constant in `app.py`) is the fixed
roster shown in every Brand dropdown, **independent of whether that brand has any ingested
data** — this was a deliberate choice so the dropdown reflects the intended future scope, not
just what happens to exist today.

- **JLT**: fully populated, 499 options, `ingest/parse_vmt.py` understands its multi-tab
  spreadsheet layout.
- **Winmate, Getac**: real spreadsheets exist in Box (see §2) but are **not ingested**. Per
  the user directly: *"the full input of these xlsx files will take more work and
  understanding as the contents are different layout than the JLT and Winmate"* — i.e.
  Winmate's own layout differs from JLT's, and presumably Getac's differs again. Each will
  need its own `parse_*.py` (or a generalized parser with per-vendor column-mapping config)
  before Technical's uploader will produce anything reliable for them today. Right now,
  uploading a Winmate/Getac file through the existing uploader will "tag whatever it happens
  to extract" with the chosen brand — described this way explicitly in the Technical page's
  own UI copy, so nobody's surprised by garbage output.
- **CipherLab**: `CipherLab Price Increase effective 4_10_2026 Product List.xlsx` exists
  in Box (see §2), but its layout differs from JLT's. No parser has been built and nothing is
  ingested yet.

Everything downstream of ingestion — approvals, Sales dropdowns, Search by Requirements,
Purchasing pricing, quote records — is brand-agnostic and will "just work" for a new brand
the moment its data is ingested with the right `brand` tag. No further plumbing should be
needed; ingestion is the actual bottleneck.

---

## 8. Non-obvious rules worth knowing before you touch this

- **Every change must be logged with author attribution.** Read `AGENTS.md` before making
  changes. Update `CHANGELOG.md` in the same branch or pull request for every code,
  configuration, data, or documentation modification. Changes made by OpenAI Codex use
  `**[Codex]**`; other people or agents must use their own clear attribution.
  Any necessary work identified but not completed—including an open PR still awaiting merge—must also be added to `CHANGELOG.md` under `Pending / TODO` and cleared with a dated, attributed entry when completed.
- **Sales Rep verification is bookkeeping, not security.** A 4-digit code with no lockout,
  no hashing (stored plaintext in `sales_reps.json`), 10,000 possible combinations. It exists
  purely so a quote records who touched it. Don't let anyone mistake it for access control.
- **Site Access PIN is a soft gate, also not real security.** A single shared 4-8 digit PIN
  (`before_request` hook in `app.py`, checked against `data/site_access.json`) protects every
  page and every `/api/*` route from casual access — meant for "don't let a random person who
  finds a shared tunnel link poke around," not real auth. `data/site_access.json` holds both
  the PIN and the Flask session secret key, is auto-generated on first run, and is **gitignored
  on purpose — this repo is public on GitHub, so that file must never be committed.** If you
  ever regenerate `.gitignore` or restructure `data/`, keep that entry.
- **Quote lock/rev rules:** a quote gets its Quote# the first time it's saved (Rev 0).
  Locking (manual toggle, or automatically on Print) "fixes" it — further edits are blocked
  until Unlock. Editing-then-saving a quote that has *ever* been locked bumps Rev by 1.
  **Only the current state of each quote is stored — there is no revision history.** Rev 0's
  content is gone the moment Rev 1 is saved over it. This is called out as a known gap in
  CHANGELOG's Pending list.
- **Accept Configuration** (Sales) is a *separate* gate from rep verification — Save needs
  both. It resets on any option change AND after every successful save (so *every* save,
  first or fifth, needs a fresh click). This was an explicit request, not an assumption.
- **Cost / Current Cost never leave Purchasing.** Not in quote snapshots, not in the printable
  view, not in the Excel export, not sent to the Sales-page JS at all
  (`CUSTOMER_FACING_PRICE_FIELDS = ["Floor Price", "MSRP"]` in `app.py` is the enforcement
  point — grep for it before adding any new customer-facing price display).
- **Uploads never erase with blanks** — re-read §5's Purchasing section. This is the fix for
  a real, previously-flagged data-loss risk; don't regress it if you touch `merge_parts()`.
- **Opportunity ID matching is exact-string, case-sensitive, not normalized.** A rep who
  types the same opportunity two different ways silently gets two different quote lineages.
  Flagged, not fixed.
- **`window.prompt()` is banned in this codebase** — it was used originally for
  Manual-Customer and Copy, and both broke silently in some browsers (prompt dialogs are
  increasingly blocked/suppressed with no error). Both were rebuilt as real inline UI. If
  you're tempted to reach for `prompt()`/`alert()`/`confirm()` anywhere in `sales.html`,
  don't — build an inline field or panel instead, same pattern as Customer/Copy/Search.

---

## 9. HubSpot / Jeeves — what stands in for them today

Nothing is connected. Every place a real integration will eventually plug in has an explicit
placeholder, not a silent gap:
- **Opportunity ID**: manually typed (§5/§8).
- **Customer**: local `customers.json` with a `source`/`hubspot_id` field ready for real data
  once a connector exists (§6) — `hubspot_id` is never set by anything today.
- **Upload button** (Sales, per-quote): calls a real endpoint
  (`/api/quotes/.../upload`) that always returns
  `{"status": "not_connected", "message": "HubSpot isn't connected yet..."}`. The button and
  wiring exist; there's nothing on the other end.
- **Email button** (Sales): downloads the real Excel export and opens the real printable
  view, but does not send anything — there's no SMTP/Outlook integration in the app itself.
- **Jeeves** (JLT's accounting/inventory system — exact product name still unconfirmed per
  the original brief): Purchasing's manual price-fill workflow is the stand-in. No connector
  research has happened in this codebase at all.

---

## 10. Known limitations / risks

- **No database, no concurrency control.** Two people editing `data/*.json` at the same
  time (e.g. two Purchasing users saving prices simultaneously) will silently last-write-wins
  clobber each other. Fine for one Box-synced folder used by a handful of people today; will
  need real locking or a DB if usage grows.
- **Flask dev server**, not production WSGI (`app.run(debug=True)` in `app.py`'s `__main__`
  block). Fine for internal prototype use, not for anything internet-facing.
- **No automated tests.** Everything in this project has been verified by hand (curl,
  browser automation, direct JSON inspection) during development, not via a test suite.
  There is no `tests/` directory.
- **`.claude/launch.json`** is specific to the Claude Code tool's browser-preview feature —
  irrelevant to running the app normally, safe to ignore or delete if not using that tool.
- **No `.gitignore`** exists yet — worth adding one for `__pycache__/`, `data/reports/`, and
  possibly the `data/*.json` runtime files themselves (open question: should real
  quote/customer/pricing data be committed to git at all, or should `data/` be seeded once
  and then gitignored so it doesn't pollute history with every price edit? Not decided —
  flagging for whoever picks this up).

---

## 11. Pending / TODO — canonical location and handling

The live, complete task list is the `## Pending / TODO` section at the top of
`CHANGELOG.md`. **Read that section directly before beginning work.** Do not assume a TODO
mentioned elsewhere in this handoff is still open, and do not maintain an independent
"complete" list here because duplicate lists drift.

At the time of this update, the changelog tracks integration work (HubSpot, Jeeves, email,
and vendor ingestion), quote revision history, storage/concurrency and production-readiness
work, test-data cleanup, the open PR awaiting merge, and the spreadsheet-ingestion risks
identified by Codex. The changelog contains the authoritative status and next action for
each item.

When new work is discovered, update `CHANGELOG.md` → `Pending / TODO` immediately if it
will not be completed in the same change. When work is completed, record the result under
the current date with author/agent attribution and close or revise the corresponding TODO.

---

## 12. If you're recreating this from zero

Order that actually worked, in case the file tree above isn't enough context on its own:

1. Parse one vendor spreadsheet into normalized JSON (`ingest/parse_vmt.py`) — prove the
   ingest step works standalone before building any UI on top of it.
2. Build Technical (approve options), Sales (pick approved options, see live price), and
   Purchasing (flag missing prices) as three thin screens against that JSON — no quote
   persistence yet, just live calculation.
3. Add quote persistence (save/load), then lock/rev semantics, then Print/Email/Upload
   stubs, then Copy — each as its own testable slice.
4. Add Customer and Sales Rep concepts, including the "not real security" rep-gate and the
   Manual-vs-Lookup customer source tracking (get the *source of truth* right here — the
   Populate-button bug in this build happened because client-side "how was this selected"
   and server-side "what is this record's real source" were conflated for a while; use the
   server's `source` field as ground truth from the start).
5. Retrofit Brand as a first-class field last, once the single-vendor version is solid — it
   touches every data file and nearly every function, so validate the single-brand version
   thoroughly first (this build did it in that order and the migration was mechanical once
   the JLT-only version worked).
6. Search by Requirements was the last major feature — it's a pure read-side feature
   (matches Technical-approved data, writes nothing) and slotted in cleanly on top of
   everything else.
