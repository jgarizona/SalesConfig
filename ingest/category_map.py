"""
Canonical category vocabulary shared across every vendor parser.

Each vendor spreadsheet spells its category labels differently (Winmate's
"Radio:" vs JLT's "Internal Wireless", for example) even when the underlying
concept - and where it should sort/filter on Sales - is the same. This module
maps a vendor's raw label to the canonical label app.py's CATEGORY_ORDER
already uses, so cross-brand sort order and "Search by Requirements" category
filtering line up regardless of which vendor an option came from.

A raw label with no entry here passes through unchanged (normalized casing/
whitespace only) rather than being dropped - it'll just sort last via
app.py's category_sort_key(), same as any other truly novel category.
"""

CANONICAL_CATEGORIES = [
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

# key: normalized (lowercased, trailing colon stripped, whitespace collapsed)
# raw label -> canonical label from CANONICAL_CATEGORIES above.
_RAW_TO_CANONICAL = {
    # Winmate
    "base unit": "Base Unit:",
    "processor": "Processor Options",
    "ram": "RAM Memory Options:",
    "memory": "RAM Memory Options:",
    "storage drive": "Storage Drive Options:",
    "storage": "Storage Drive Options:",
    "micros sd memory": "Storage Drive Options:",
    "micro sd memory": "Storage Drive Options:",
    "display": "Display options:",
    "display option": "Display options:",
    "lcd": "Display options:",
    "ant options": "Internal Wireless",
    "antenna options": "Internal Wireless",
    # "DIDO", "CANBUS", "LAN" deliberately NOT collapsed into one bucket -
    # same reused-code collision risk as Camera/Data Collection above.
    "accessories": "Add On Options:",
    "accessory": "Add On Options:",
    # "Data Collection:" and "Camera" are deliberately NOT mapped onto
    # "Add On Options:" - both use small reused codes (X/A/1/2) that are
    # only unique within their own original narrow category. Folding them
    # into the same canonical bucket as the flat Accessories section (which
    # uses globally-unique SKU-shaped codes) created real (brand, platform,
    # category, code) collisions that silently dropped catalog options on
    # merge - confirmed 2026-08-15 (12 Winmate options vanished this way
    # before this was caught). Left as distinct pass-through categories
    # instead; each stays internally unique even though it doesn't match
    # JLT's canonical vocabulary.
    "radio": "Internal Wireless",
    "wireless": "Internal Wireless",
    "wlan": "Internal Wireless",
    "ip rating": "IP Rating Options:",
    "power cable": "Power Cable Options:",
    "power": "Power Cable Options:",
    "os": "Operating System:",
    "operating system": "Operating System:",
    "windows": "Operating System:",
    # CipherLab (Model Code suffix, not a real column - see parse_cipherlab.py)
    "product": "Base Unit:",
    "accessory": "Add On Options:",
    "adapter": "Add On Options:",
    "software": "Operating System:",
    "advantage": "Add On Options:",  # CipherLab extended-warranty/service plans
}


def normalize_key(raw_label):
    return (raw_label or "").strip().rstrip(":").strip().lower()


def to_canonical(raw_label):
    """Best-effort map of a vendor's raw category label to the canonical
    vocabulary. Falls back to the raw label (stripped) if no mapping is
    known, so nothing silently disappears - it just won't group with an
    existing category."""
    if not raw_label:
        return raw_label
    key = normalize_key(raw_label)
    return _RAW_TO_CANONICAL.get(key, raw_label.strip())
