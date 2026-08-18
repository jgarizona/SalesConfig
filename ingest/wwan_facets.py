"""
Shared WWAN (cellular) facet extraction for Search by Requirements'
"Internal Wireless" field. Per the user (2026-08-18): WWAN/cellular info is
mixed in with WiFi/Bluetooth/GPS in the same free-text description, and the
carrier/module should be searchable separately from generation.

Unlike storage/OS, "Internal Wireless" is NOT replaced by these two facets
- a raw description here can simultaneously describe WiFi standard,
Bluetooth version, GPS, AND cellular (e.g. "WLAN (802.11 a/b/g/n/ac) + BT
5.0 + GPS 4G Sierra EM7455"), so removing the flat field would lose real
search capability (a rep searching by WiFi standard or Bluetooth version).
These two facets are ADDED alongside the existing flat "Internal Wireless"
list, extracted only where present - most rows have no WWAN component at
all, and won't get a value for either.

Generation: 3G/4G/5G, checked 5G-first (LTE counts as 4G).

Carrier: named US carriers (AT&T/T-Mobile/Verizon, present on Intel
Wireless 8265/AX210 module SKUs) or a specific cellular module part number
(Telit LN920, Sierra EM7455/EM7411/EM9291/EM7595, Quectel RedCap, etc.).
Built by reviewing all 109 distinct real "Internal Wireless" values in the
catalog as of 2026-08-18 (see CHANGELOG.md). Deliberately does NOT merge
EM7455/MC7455 or EM7411/MC7411 - those are different Sierra Wireless part
numbers (M.2 vs mini-PCIe form factor) even though same chip family, and
nothing in the source text confirms they're interchangeable for search
purposes the way "Elkhart Lake" confirmed two CPU spellings were the same
chip. A row with a generation but no named carrier/module (common - many
rows just say "4G" or "5G WWAN" with nothing more specific) is only
findable via Generation, same as an untagged storage/OS description.
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


# Checked in order - named carriers first, then specific module part
# numbers (each kept distinct per its real part number, not merged across
# similar-looking ones - see module docstring).
_CARRIER_PATTERNS = [
    ("AT&T", re.compile(r"AT&T", re.IGNORECASE)),
    ("T-Mobile", re.compile(r"T-Mobile", re.IGNORECASE)),
    ("Verizon", re.compile(r"Verizon", re.IGNORECASE)),
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


def extract_wwan_carrier(text):
    if not text:
        return None
    for label, pat in _CARRIER_PATTERNS:
        if pat.search(text):
            return label
    return None
