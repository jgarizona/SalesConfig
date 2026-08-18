"""
Shared storage-spec parsing, used both at ingest time (Getac precomputes a
`storage`/`storage_tech` attribute pair the same way it does cpu/os/ram) and
at live search time (app.py derives the same two facets from JLT/Winmate's
real "Storage Drive Options:" rows on the fly, since those are real
per-category options with no precomputed attributes dict).

Splits a free-text storage description into two independent facets a rep
actually searches on - Capacity and Technology (interface/media type) -
instead of requiring an exact match against the full description. Across
JLT+Winmate's real catalog this matters two ways (per the user, 2026-08-17):
a rep searching by capacity shouldn't have to separately care whether it's
SSD/CFAST/eMMC/etc, and a rep searching by technology (e.g. "M.2") wants
every M.2 drive regardless of capacity - a single flat "Storage Drive
Options:" dropdown of full descriptions could do neither.
"""

import re

# Industry-standard "same tier, different rounding convention" pairs -
# 60GB/64GB, 120GB/128GB, etc. are marketed as different numbers by
# different vendors (or even the same vendor across product lines) for
# what's functionally the same capacity class. Collapsed to the larger
# (binary-GB) label so a search on either number finds both.
_CAPACITY_TIER_ALIASES_GB = {60: 64, 120: 128, 240: 256, 480: 512, 960: 1024}

_CAPACITY_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(GB|G|TB|T)\b", re.IGNORECASE)


def extract_storage_capacity(text):
    """'M.2 60GB' / '64 GB eMMC' / '1 TB  M.2 NVMe SSD' -> '64GB' / '64GB' / '1TB'.
    Requires a unit suffix directly after the number, so an M.2 form-factor
    code like "2242" in "M.2 2242 SSD 128GB" is correctly skipped in favor
    of the real capacity later in the string."""
    if not text:
        return None
    m = _CAPACITY_RE.search(text)
    if not m:
        return None
    num, unit = float(m.group(1)), m.group(2).upper()
    gb = round(num * 1024) if unit in ("TB", "T") else round(num)
    gb = _CAPACITY_TIER_ALIASES_GB.get(gb, gb)
    if gb >= 1024 and gb % 1024 == 0:
        return f"{gb // 1024}TB"
    return f"{gb}GB"


# Checked in this order - "M.2" wins over "SSD" even though most M.2 options
# also say SSD/NVMe/SATA, since a rep filtering by M.2 wants every M.2 drive
# regardless of which of those it also mentions.
_TECHNOLOGY_PATTERNS = [
    ("M.2", re.compile(r"M\.2", re.IGNORECASE)),
    ("mSATA", re.compile(r"mSATA", re.IGNORECASE)),
    ("CFAST", re.compile(r"CFAST", re.IGNORECASE)),
    ("eMMC", re.compile(r"eMMC", re.IGNORECASE)),
    ("Micro SD", re.compile(r"Micro\s*SD", re.IGNORECASE)),
    ("NVMe", re.compile(r"NVMe", re.IGNORECASE)),
    ("SSD", re.compile(r"\bSSD\b", re.IGNORECASE)),
]


def extract_storage_technology(text):
    """'256GB M.2 NVMe SSD' -> 'M.2'; '64GB eMMC' -> 'eMMC'; '128 GB' -> None
    (no technology stated in the source text - only searchable by capacity)."""
    if not text:
        return None
    for label, pat in _TECHNOLOGY_PATTERNS:
        if pat.search(text):
            return label
    return None
