"""HubSpot integration - the only module allowed to talk to HubSpot directly.

Not wired to any UI element yet. See HANDOFF.md §9 for the full plan this
implements and CHANGELOG.md's 2026-08-25 entry for what's still unverified.
Nothing here can be exercised until data/hubspot_config.json has a real
Private App access token in it - see HANDOFF.md §9's setup checklist for how
to get one. Every function below raises HubSpotNotConfigured until then.

Two things are called out inline below as unverified, because there is no
token yet to test against a live account:
- ASSOCIATION_TYPE_LINE_ITEM_TO_DEAL / ASSOCIATION_TYPE_NOTE_TO_DEAL are
  HubSpot's documented default association type IDs for these object pairs,
  not something confirmed against JLT's own portal.
- push_quote_to_deal()'s default amount_field ("floor_total" vs "msrp_total")
  is a guess at which of the app's two totals should become the Deal's
  amount - confirm with Jeff before relying on it.

Also unconfirmed: whether app-eu1.hubspot.com (JLT's portal, EU-hosted)
needs a different API base than the default HUBSPOT_API_BASE below - check
with HubSpot support/docs before the first real call, per HANDOFF.md §9.
"""

import json
import os
import time
from pathlib import Path

import requests

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
HUBSPOT_CONFIG_FILE = DATA_DIR / "hubspot_config.json"

HUBSPOT_API_BASE = "https://api.hubapi.com"
REQUEST_TIMEOUT = 20  # seconds

# HubSpot-defined default association type IDs (see module docstring - not
# yet verified against a live account, since there's no token to test with).
ASSOCIATION_TYPE_LINE_ITEM_TO_DEAL = 20
ASSOCIATION_TYPE_NOTE_TO_DEAL = 214

# Deal properties pulled back on every deal lookup - hs_is_closed is what
# open/closed filtering keys on, since dealstage IDs vary per pipeline and
# can't be checked generically the way a single boolean can.
DEAL_LOOKUP_PROPERTIES = ["dealname", "dealstage", "amount", "hs_is_closed", "closedate"]


class HubSpotError(Exception):
    """Any failure talking to HubSpot - bad token, missing scope, a rejected
    request, or a network error. Callers (the Flask routes) should catch
    this and show the rep a real error, never swallow it as success."""


class HubSpotNotConfigured(HubSpotError):
    """No Private App access token has been set up yet. Expected state
    until someone completes the checklist in HANDOFF.md §9 - not a bug."""


# --------------------------------------------------------------- token config
# Same treatment as app.py's site_access.json: gitignored, auto-created with
# a blank token on first read so the file always exists and every caller has
# one place to look. See HANDOFF.md §9 for how the real token gets in here.

def load_or_create_hubspot_config():
    if HUBSPOT_CONFIG_FILE.exists():
        return json.loads(HUBSPOT_CONFIG_FILE.read_text(encoding="utf-8"))
    config = {"access_token": None}
    save_hubspot_config(config)
    return config


def save_hubspot_config(config):
    HUBSPOT_CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")


def get_access_token():
    """HUBSPOT_ACCESS_TOKEN env var wins if set (handy for local testing
    without editing the config file); otherwise reads
    data/hubspot_config.json. Raises HubSpotNotConfigured if neither has a
    real token yet."""
    env_token = os.environ.get("HUBSPOT_ACCESS_TOKEN", "").strip()
    if env_token:
        return env_token
    token = (load_or_create_hubspot_config().get("access_token") or "").strip()
    if not token:
        raise HubSpotNotConfigured(
            "No HubSpot access token configured yet. Create a Private App "
            "and paste its token into data/hubspot_config.json's "
            "\"access_token\" field - see HANDOFF.md §9 for the full "
            "checklist."
        )
    return token


# ------------------------------------------------------------------ requests

def _headers():
    return {"Authorization": f"Bearer {get_access_token()}"}


def _raise_for_response(resp):
    if resp.ok:
        return
    try:
        detail = resp.json().get("message", resp.text)
    except ValueError:
        detail = resp.text
    raise HubSpotError(f"HubSpot API error {resp.status_code} on {resp.request.method} "
                        f"{resp.request.url}: {detail}")


def _request(method, path, **kwargs):
    url = f"{HUBSPOT_API_BASE}{path}"
    try:
        resp = requests.request(
            method, url, headers=_headers(), timeout=REQUEST_TIMEOUT, **kwargs,
        )
    except requests.RequestException as exc:
        raise HubSpotError(f"Network error calling HubSpot ({method} {path}): {exc}") from exc
    _raise_for_response(resp)
    return resp.json() if resp.content else {}


def _numeric_price(value):
    """Mirrors app.py's money_value() - "Incl"/"NC" and blanks all become 0
    so a HubSpot line item never gets a garbage/non-numeric price."""
    if value in (None, ""):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip().upper()
    if s in ("INCL", "NC"):
        return 0.0
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return 0.0


# ----------------------------------------------------- 1. customer/company lookup

def search_customers(query, limit=10):
    """Searches HubSpot Companies, not Contacts - JLT's customers.json
    stores a single flat name per customer (no first/last name), which maps
    onto a Company record, not a person. Company is also where the existing
    Jeeves linkage fields live (see HANDOFF.md §9), which a Contact-based
    lookup would miss entirely."""
    body = {
        "filterGroups": [{"filters": [
            {"propertyName": "name", "operator": "CONTAINS_TOKEN", "value": query},
        ]}],
        "properties": ["name", "domain"],
        "limit": limit,
    }
    data = _request("POST", "/crm/v3/objects/companies/search", json=body)
    return [
        {
            "id": r["id"],
            "name": r.get("properties", {}).get("name"),
            "domain": r.get("properties", {}).get("domain"),
        }
        for r in data.get("results", [])
    ]


# --------------------------------------------------------------- 2. deal lookup

def get_open_deals_for_company(company_id):
    """Follows HubSpot's real association graph rather than searching by
    name - see HANDOFF.md §9 for why a name search was ruled out. Returns
    only open deals (hs_is_closed != true), since a closed deal isn't a
    candidate to attach a new configuration to."""
    assoc = _request("GET", f"/crm/v4/objects/company/{company_id}/associations/deal")
    deal_ids = [str(r["toObjectId"]) for r in assoc.get("results", [])]
    if not deal_ids:
        return []

    body = {
        "properties": DEAL_LOOKUP_PROPERTIES,
        "inputs": [{"id": deal_id} for deal_id in deal_ids],
    }
    data = _request("POST", "/crm/v3/objects/deals/batch/read", json=body)

    open_deals = []
    for r in data.get("results", []):
        props = r.get("properties", {})
        if str(props.get("hs_is_closed")).lower() == "true":
            continue
        open_deals.append({
            "id": r["id"],
            "name": props.get("dealname"),
            "stage": props.get("dealstage"),
            "amount": props.get("amount"),
            "close_date": props.get("closedate"),
        })
    return open_deals


# --------------------------------------------------- 3. push quote -> deal

def push_quote_to_deal(deal_id, quote, amount_field="floor_total"):
    """Creates one HubSpot line item per quote selection (associated to the
    deal) and updates the deal's amount to match. amount_field picks which
    of the quote's two totals ("floor_total" or "msrp_total") becomes both
    the deal amount and each line item's unit price - see this module's
    docstring, this default has not been confirmed with Jeff."""
    price_key = "MSRP" if amount_field == "msrp_total" else "Floor Price"

    line_item_inputs = []
    for line in quote.get("selections", []):
        line_item_inputs.append({
            "properties": {
                "name": line.get("description", line.get("code", "")),
                "hs_sku": line.get("code"),
                "quantity": "1",
                "price": str(_numeric_price(line.get(price_key))),
            },
            "associations": [{
                "to": {"id": deal_id},
                "types": [{
                    "associationCategory": "HUBSPOT_DEFINED",
                    "associationTypeId": ASSOCIATION_TYPE_LINE_ITEM_TO_DEAL,
                }],
            }],
        })

    line_item_ids = []
    if line_item_inputs:
        created = _request(
            "POST", "/crm/v3/objects/line_items/batch/create",
            json={"inputs": line_item_inputs},
        )
        line_item_ids = [r["id"] for r in created.get("results", [])]

    total = quote.get(amount_field, 0)
    _request(
        "PATCH", f"/crm/v3/objects/deals/{deal_id}",
        json={"properties": {"amount": str(total)}},
    )

    return {"deal_id": deal_id, "line_item_ids": line_item_ids, "amount": total}


# ------------------------------------------------- 4/5. attach a file to a deal

def attach_file_to_deal(deal_id, file_bytes, filename, note_body=None):
    """Shared by both file-attach interactions in HANDOFF.md §9 (the
    pricing export and the rep's own final quote document) - HubSpot
    doesn't distinguish app-generated from human-made, it's just a file."""
    upload = _request(
        "POST", "/files/v3/files",
        files={"file": (filename, file_bytes)},
        data={"options": json.dumps({"access": "PRIVATE"})},
    )
    file_id = upload["id"]

    note_properties = {
        "hs_note_body": note_body or f"Attached from SalesConfig: {filename}",
        "hs_timestamp": str(int(time.time() * 1000)),
        "hs_attachment_ids": file_id,
    }
    note = _request(
        "POST", "/crm/v3/objects/notes",
        json={
            "properties": note_properties,
            "associations": [{
                "to": {"id": deal_id},
                "types": [{
                    "associationCategory": "HUBSPOT_DEFINED",
                    "associationTypeId": ASSOCIATION_TYPE_NOTE_TO_DEAL,
                }],
            }],
        },
    )

    return {"file_id": file_id, "note_id": note["id"]}
