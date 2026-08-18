"""
Shared CPU-label cleanup for Search by Requirements' "Processor Options"
field. Unlike storage/OS, a CPU model name has no predictable structure to
regex-extract a clean facet from - "Intel 6413E", "i7-7600U", and "Qualcomm
QCS6490" don't share a pattern the way "64GB" or "Windows 11" do. So this
does NOT split into two facets; it only collapses near-duplicate spellings
of the *same* real chip into one canonical label, in two tiers:

1. A mechanical pass (`_mechanical_normalize`) that's always safe: strips
   trademark symbols (R/TM), an invisible soft-hyphen character found in one
   real description, collapses whitespace runs, and drops a trailing
   "(Optional)"/"(option)"/"No Longer available" annotation. This alone
   merges purely cosmetic duplicates (e.g. "i7-7600U" and "i7-7600U No
   Longer available") without any risk of merging two actually-different
   chips.

2. A small hand-curated alias table (`_CPU_ALIASES`, keyed on the
   mechanically-normalized form) for duplicates that only a human can
   safely confirm are the same real chip - e.g. "Intel 6413E" and "Intel
   6413E Elkhart Lake" refer to the same Atom x6413E (Elkhart Lake is
   Intel's codename for it), but nothing about the text alone proves that;
   a blind fuzzy-match risked merging genuinely different chips (a real
   near-miss found while auditing the data: "Qualcomm 660"/"Snapdragon 660"
   describes a different, older SoC than "Qualcomm QCS6490", despite both
   being "Qualcomm" - only the model number tells them apart). Built by
   manually reviewing all 55 distinct real "Processor Options" values in
   the catalog as of 2026-08-18 (see CHANGELOG.md) - confirmed with the
   user before merging any group. One deliberately excluded pair: "ARM 2 x
   A78 2.0GHz + 4 x A55 2.0GHz" and "ARM Genio 510 2 x A78 2.0GHz + 4 x A55
   2.0GH" have identical core configs and look like the same chip
   (MediaTek Genio 510), but that core layout isn't unique to one SoC, so
   they're left as distinct entries rather than guessed at.
"""

import re

_TRADEMARK_RE = re.compile(r"[®™]")  # (R) and (TM) symbols
_SOFT_HYPHEN_RE = re.compile(r"\xad")
_WS_RE = re.compile(r"\s+")
_TRAILING_FILLER_RE = re.compile(
    r"\s*[,]?\s*(?:\(optional\)|\(option\)|no longer available)\s*$", re.IGNORECASE
)


def _mechanical_normalize(text):
    if not text:
        return text
    t = _SOFT_HYPHEN_RE.sub("", text)
    t = _TRADEMARK_RE.sub("", t)
    prev = None
    while prev != t:
        prev = t
        t = _TRAILING_FILLER_RE.sub("", t)
    return _WS_RE.sub(" ", t).strip()


# key: mechanically-normalized raw description -> curated canonical label.
_CPU_ALIASES = {
    # Intel Atom x6413E (Elkhart Lake)
    "Intel 6413E": "Intel Atom x6413E (Elkhart Lake)",
    "Intel 6413E Elkhart Lake": "Intel Atom x6413E (Elkhart Lake)",
    "Intel 6413E Elkhart lake": "Intel Atom x6413E (Elkhart Lake)",
    "Intel Atom x6413E (Long Lead Time)": "Intel Atom x6413E (Elkhart Lake)",
    # Intel Atom x6425E (Elkhart Lake)
    "Intel Elkhart Lake x6425E Processor , 2.0 GHz turbo up to a max of 3.0GHz":
        "Intel Atom x6425E (Elkhart Lake)",
    "Intel Elkhart lake x6425E": "Intel Atom x6425E (Elkhart Lake)",
    # Intel Pentium N4200 (Apollo Lake)
    "1.1GHz Intel Pentium N4200 Processor": "Intel Pentium N4200 (Apollo Lake)",
    "Intel Apollo Lake Pentium n4200 Processor": "Intel Pentium N4200 (Apollo Lake)",
    # Intel Celeron N6211 (Elkhart Lake)
    "Intel Celeron N6211": "Intel Celeron N6211 (Elkhart Lake)",
    "Intel Elkhart Lake Celeron N6211 Processor": "Intel Celeron N6211 (Elkhart Lake)",
    # Intel Core i5-1235U (Alder Lake)
    "Intel Core i5-1235U (up to 4.4GHz)": "Intel Core i5-1235U (Alder Lake)",
    "Intel Core i5-1235U Alder Lake processor": "Intel Core i5-1235U (Alder Lake)",
    "Intel Core i5-1235U, up to 4.40GHz": "Intel Core i5-1235U (Alder Lake)",
    # Intel Atom E3845
    "Intel Quad-Core Atom E3845 Processor, 1.91 GHz": "Intel Atom E3845",
    "Intel Quad-Core E3845": "Intel Atom E3845",
    # Qualcomm Snapdragon 660
    "Qualcomm 660": "Qualcomm Snapdragon 660",
    "Qualcomm Snapdragon 660": "Qualcomm Snapdragon 660",
    "Qualcomm Snapdragon 660, Octa-core up to 2.2 GHz": "Qualcomm Snapdragon 660",
    "Qualcomm SDA660 Kryo 260 CPU + Octacore up to 2.2GHz": "Qualcomm Snapdragon 660",
    # Qualcomm QCS6490
    "Qualcomm QCS6490": "Qualcomm QCS6490",
    "Qualcomm 6490 (OctaCore 2.7GHz)": "Qualcomm QCS6490",
}

# The set of canonical labels above that represent a curated multi-variant
# merge - used to sort these first in the dropdown, with everything else
# (already-unique labels, and ones only the mechanical pass touched) after.
CURATED_CANONICAL_LABELS = frozenset(_CPU_ALIASES.values())


def normalize_cpu_label(text):
    if not text:
        return None
    mechanical = _mechanical_normalize(text)
    return _CPU_ALIASES.get(mechanical, mechanical)


def cpu_sort_key(label):
    """Curated (deduped-group) labels first, alphabetically; then every
    other label, alphabetically - per the user, 2026-08-18."""
    return (0 if label in CURATED_CANONICAL_LABELS else 1, label)
