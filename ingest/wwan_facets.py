"""
Shared WWAN (cellular) facet extraction for Search by Requirements'
"Internal Wireless" field. Per the user (2026-08-18): WWAN/cellular info is
mixed in with WiFi/Bluetooth/GPS in the same free-text description, and the
carrier/module should be searchable separately from generation.

Unlike storage/OS, "Internal Wireless" is NOT replaced by these facets - a
raw description here can simultaneously describe WiFi standard, Bluetooth
version, GPS, AND cellular (e.g. "WLAN (802.11 a/b/g/n/ac) + BT 5.0 + GPS
4G Sierra EM7455"), so removing the flat field would lose real search
capability (a rep searching by WiFi standard or Bluetooth version). These
facets are ADDED alongside the existing flat "Internal Wireless" list,
extracted only where present - most rows have no WWAN component at all,
and won't get a value for any of them.

Three extractors, feeding two synthetic search categories:

- `extract_wwan_generation` -> 3G/4G/5G (LTE counts as 4G).
- `extract_wwan_module` -> a specific cellular module part number (Telit
  LN920/FN990, Sierra EM7455/EM7411/EM9291/EM7595/MC7455/MC7411, Quectel
  RedCap, MediaTek, HUAWEI). Feeds into "WWAN Generation" alongside
  `extract_wwan_generation`, not its own category - per the user
  (2026-08-18), a specific module identifies a generation more directly
  than it identifies a carrier ("the cards are tied to 3g 4g 5g more than
  the carrier"), so module names are offered as additional, more specific
  values within the same Generation dropdown (sorted after the plain
  3G/4G/5G entries - see `wwan_generation_sort_key`), not mixed into
  Carrier. Deliberately does NOT merge EM7455/MC7455 or EM7411/MC7411 -
  different Sierra Wireless part numbers (M.2 vs mini-PCIe form factor),
  and nothing in the source text confirms they're interchangeable for
  search the way "Elkhart Lake" confirmed two CPU spellings were the same
  chip.
- `extract_wwan_carrier` -> only a named US carrier (AT&T/T-Mobile/
  Verizon), present on Intel Wireless 8265/AX210 module SKUs. Kept as its
  own "WWAN Carrier" category, separate from module part numbers.

Built by reviewing all 109 distinct real "Internal Wireless" values in the
catalog as of 2026-08-18 (see CHANGELOG.md). A row with a generation but no
named module (common - many rows just say "4G" or "5G WWAN" with nothing
more specific) is only findable via the plain generation value, same as an
untagged storage/OS description.
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
    """Plain generations first (3G, 4G, 5G in that order), then module part
    numbers alphabetically after - per the user, 2026-08-18."""
    if label in _GENERATION_SORT_ORDER:
        return (0, _GENERATION_SORT_ORDER[label])
    return (1, label)


# Specific cellular module part numbers - NOT named carriers, see module
# docstring for why these feed "WWAN Generation" rather than "WWAN Carrier".
_MODULE_PATTERNS = [
    ("Telit LN920", re.compile(r"Telit\s*LN920", re.IGNORECASE)),
    ("Telit FN990", re.compile(r"Telit\s*FN990", re.IGNORECASE)),
    ("Sierra EM7595", re.compile(r"(?:Sierra\s*)?EM7595", re.IGNORECASE)),
    ("Sierra EM9291", re.compile(r"(?:Sierra\s*)?EM9291", re.IGNORECASE)),
    ("Sierra EM7455", re.compile(r"(?:Sierra\s*)?EM7455", re.IGNORECASE)),
    ("Sierra MC7455", re.compile(r"(?:Sierra\s*)?MC7455", re.IGNORECASE)),
    ("Sierra EM7411", re.compile(r"(?:Sierra\s*)?EM7411", re.IGNORECASE)),
    ("Sierra MC7411", re.compile(r"(?:Sierra\s*)?MC7411", re.IGNORECASE)),
    ("Quectel RedCap", re.compile(r"Quectel\s*RedCap", re.IGNORECASE)),
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


def extract_wwan_carrier(text):
    if not text:
        return None
    for label, pat in _CARRIER_PATTERNS:
        if pat.search(text):
            return label
    return None
