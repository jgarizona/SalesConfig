"""
WiFi-only facet extraction for Search by Requirements' "Internal Wireless"
field. Per the user (2026-08-18): JLT/Winmate's real "Internal Wireless"
category mixes WiFi radio, Bluetooth, GPS, and WWAN cellular info into one
free-text description (e.g. "Intel Wireless AX210 802.11 ac/a/b/g/n with
WWAN *AT&T*"), but the "Internal Wireless" search field itself should be
WiFi-only - the WWAN generation/card/carrier are their own separate fields
(see wwan_facets.py). This is what used to be handled by keeping the raw
flat description list alongside the WWAN facets (see git history around
2026-08-18); that's been replaced by this extractor so "Internal Wireless"
only ever shows a clean WiFi answer.

Two brands, two different levels of detail in the source text:
- JLT names a specific Intel chip model (AX210, 8265) - checked first,
  since a rep searching by "AX210" wants the exact chip, not just "this
  supports 802.11ax".
- Winmate never names a chip, only the 802.11 standard revision (ac/ax/n)
  - falls back to that when no chip model is present. A row mentioning
  several revisions (e.g. "802.11 a/b/g/n,ac/ax") returns only the highest
  one, since that revision implies backward compatibility with the rest.

Returns None (not a fabricated "unspecified" bucket) for rows with no WiFi
component at all (e.g. JLT's "WWAN Sierra wireless EM7455", a WWAN-module-
only row) or a bare "WLAN"/"Wifi" mention with no standard stated - those
rows are still fully selectable directly from the platform's own option
list on Sales, they just can't be found via this search facet.
"""

import re

_CHIPSET_PATTERNS = [
    ("Intel AX210", re.compile(r"AX210", re.IGNORECASE)),
    ("Intel 8265", re.compile(r"\b8265\b", re.IGNORECASE)),
]

_NO_RADIO_RE = re.compile(r"No\s*(Radio|WLAN|Wi[- ]?Fi|Adapter)", re.IGNORECASE)

# Ordered highest-to-lowest so a row listing several revisions ("a/b/g/n,ac")
# resolves to the newest one it supports.
_STANDARD_ORDER = ["ax", "ac", "n", "g", "b"]
_STANDARD_SEGMENT_RE = re.compile(r"802\.11\s*([abcgnx/,\s]+)", re.IGNORECASE)


def extract_wifi_radio(text):
    if not text:
        return None
    for label, pat in _CHIPSET_PATTERNS:
        if pat.search(text):
            return label
    if _NO_RADIO_RE.search(text):
        return "No Radio"
    m = _STANDARD_SEGMENT_RE.search(text)
    if m:
        segment = m.group(1).lower()
        for std in _STANDARD_ORDER:
            if std in segment:
                return f"802.11{std}"
    return None
