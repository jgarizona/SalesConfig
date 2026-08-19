"""
Shared WWAN (cellular) facet extraction for Search by Requirements'
"Internal Wireless" field. Per the user (2026-08-18): WWAN/cellular info is
mixed in with WiFi/Bluetooth/GPS in the same free-text description, and the
carrier/module should be searchable separately from generation - and from
each other. "Internal Wireless" itself is now WiFi-only (see
ingest/wifi_facets.py); these three extractors feed three independent WWAN
search fields instead.

- `extract_wwan_generation` -> 3G/4G/5G (LTE counts as 4G).
- `extract_wwan_module` -> a specific cellular module/card part number
  (Telit LN920/FN990, Sierra EM7455/EM7411/EM9291/EM7595/MC7455/MC7411/
  MC7421, Quectel RedCap/RedCap RG255C, MediaTek, HUAWEI). Its own "WWAN
  Card" category (revised 2026-08-18, per the user - originally folded into
  "WWAN Generation" as extra, more-specific values, but a rep looking for a
  specific card wants its own dropdown rather than hunting through
  Generation's 3G/4G/5G list). Deliberately does NOT merge EM7455/MC7455 or
  EM7411/MC7411 - different Sierra Wireless part numbers (M.2 vs mini-PCIe
  form factor), and nothing in the source text confirms they're
  interchangeable for search the way "Elkhart Lake" confirmed two CPU
  spellings were the same chip. "Quectel RedCap RG255C" is checked before
  the bare "Quectel RedCap" pattern so a row naming the specific submodel
  gets the more precise label.
- `extract_wwan_carrier` -> only a named US carrier (AT&T/T-Mobile/
  Verizon), present on Intel Wireless 8265/AX210 module SKUs. Kept as its
  own "WWAN Carrier" category, separate from module part numbers.

Built by reviewing all 109 distinct real "Internal Wireless" values in the
catalog as of 2026-08-18 (see CHANGELOG.md). A row with a generation but no
named module (common - many rows just say "4G" or "5G WWAN" with nothing
more specific) is only findable via the plain generation value, same as an
untagged storage/OS description. MC7421 and the RG255C submodel aren't in
the catalog as of 2026-08-18 (only MC7411 appears) - patterns added ahead
of time per the user, so a future spreadsheet update picks them up without
another code change.
"""

import re

_GEN_PATTERNS = [
    ("5G", re.compile(r"5G", re.IGNORECASE)),
    ("4G", re.compile(r"4G|LTE", re.IGNORECASE)),
    ("3G", re.compile(r"3G", re.IGNORECASE)),
]


def extract_wwan_generation(text):
    if not text:
        return None
    for label, pat in _GEN_PATTERNS:
        if pat.search(text):
            return label
    return None


_GENERATION_SORT_ORDER = {"3G": 0, "4G": 1, "5G": 2}


def wwan_generation_sort_key(label):
    """3G, 4G, 5G in that order (module part numbers used to live in this
    same dropdown and sort alphabetically after - see "WWAN Card" now, this
    fallback branch is unreachable for real data but kept harmless)."""
    if label in _GENERATION_SORT_ORDER:
        return (0, _GENERATION_SORT_ORDER[label])
    return (1, label)


# Specific cellular module/card part numbers - NOT named carriers, see
# module docstring for why these feed their own "WWAN Card" category rather
# than "WWAN Carrier". Per the user (2026-08-18): "Quectel RedCap" always
# means the RG255C part - there's no separate bare "Quectel RedCap" product,
# so a row naming either the plain family name or the specific submodel gets
# the same full label, unlike the Sierra/Telit entries which stay split by
# real distinct part number.
_MODULE_PATTERNS = [
    ("Telit LN920", re.compile(r"Telit\s*LN920", re.IGNORECASE)),
    ("Telit FN990", re.compile(r"Telit\s*FN990", re.IGNORECASE)),
    ("Sierra EM7595", re.compile(r"(?:Sierra\s*)?EM7595", re.IGNORECASE)),
    ("Sierra EM9291", re.compile(r"(?:Sierra\s*)?EM9291", re.IGNORECASE)),
    ("Sierra EM7455", re.compile(r"(?:Sierra\s*)?EM7455", re.IGNORECASE)),
    ("Sierra MC7455", re.compile(r"(?:Sierra\s*)?MC7455", re.IGNORECASE)),
    ("Sierra EM7411", re.compile(r"(?:Sierra\s*)?EM7411", re.IGNORECASE)),
    ("Sierra MC7411", re.compile(r"(?:Sierra\s*)?MC7411", re.IGNORECASE)),
    ("Sierra MC7421", re.compile(r"(?:Sierra\s*)?MC7421", re.IGNORECASE)),
    ("Quectel RedCap RG255C", re.compile(r"Quectel\s*RedCap(\s*RG255C)?", re.IGNORECASE)),
    ("MediaTek", re.compile(r"MediaTek|\bMTK\b", re.IGNORECASE)),
    ("HUAWEI", re.compile(r"HUAWEI", re.IGNORECASE)),
]


def extract_wwan_module(text):
    if not text:
        return None
    for label, pat in _MODULE_PATTERNS:
        if pat.search(text):
            return label
    return None


# Named US carriers only - module part numbers are NOT included here, see
# module docstring.
_CARRIER_PATTERNS = [
    ("AT&T", re.compile(r"AT&T", re.IGNORECASE)),
    ("T-Mobile", re.compile(r"T-Mobile", re.IGNORECASE)),
    ("Verizon", re.compile(r"Verizon", re.IGNORECASE)),
]

# A row can say "WWAN"-capable (e.g. an external WWAN antenna connector)
# without naming a carrier OR a specific module - per the user (2026-08-18),
# these get a 4th "Generic" carrier value rather than no value at all. Only
# fires when no named carrier AND no named module matched - a module-only
# row ("4G WWAN Telit LN920...") is findable via WWAN Card, not this.
_GENERIC_WWAN_RE = re.compile(r"WWAN|^Generic$", re.IGNORECASE)


def extract_wwan_carrier(text):
    """Idempotent on its own output - JLT's real WWAN Carrier rows had their
    description field cleaned up (2026-08-18) to just the carrier name
    itself ("AT&T", "Generic", etc., replacing the original full sentence),
    and this function still needs to recognize that already-clean text on
    every later call (Search facet computation reruns it against whatever
    the current description is - see FACET_CATEGORIES in app.py), not just
    the original raw vendor text with "WWAN" and no carrier/module named."""
    if not text:
        return None
    for label, pat in _CARRIER_PATTERNS:
        if pat.search(text):
            return label
    if _GENERIC_WWAN_RE.search(text) and extract_wwan_module(text) is None:
        return "Generic"
    return None
