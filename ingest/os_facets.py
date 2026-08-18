"""
Shared operating-system-spec parsing, used both at ingest time (Getac
precomputes an `os_version`/`os_edition` attribute pair the same way it
does cpu/ram/storage/etc) and at live search time (app.py derives the same
two facets from JLT/Winmate's real "Operating System:" rows on the fly,
since those are real per-category options with no precomputed attributes
dict).

Splits a free-text OS description into two independent facets a rep
actually searches on - Version and Edition (licensing/servicing channel) -
instead of requiring an exact match against the full description. Per the
user (2026-08-17): when someone's looking at Windows or Android, they
don't care about GAC vs LTSC, and they definitely don't care about a CPU
model that happens to be mentioned in the same string (real example from
the catalog: "Windows 11 IoT Enterprise LTSC  i7-1185GRE") - they just want
Windows 10, Windows 11, Android 12, etc., the same way the Processor
Options list already gives them clean CPU model names to pick from.
"""

import re

_ANDROID_RE = re.compile(r"Android\s*(\d+)(?:\.0)?", re.IGNORECASE)
_WINDOWS_RE = re.compile(r"Win(?:dows)?\s*(\d+)", re.IGNORECASE)
_LINUX_RE = re.compile(r"(Linux\s+\S+\s+[\d.]+)", re.IGNORECASE)


def extract_os_version(text):
    """'Windows 11 IoT Enterprise LTSC  i7-1185GRE' -> 'Windows 11';
    'Android 11.0' -> 'Android 11' (trailing '.0' dropped so it doesn't
    fragment from plain 'Android 11'); 'Linux Ubuntu 20.04' -> unchanged.
    CPU mentions elsewhere in the text (e.g. the i7-1185GRE above) are
    never matched by these patterns, so they're silently ignored rather
    than corrupting the version - that info belongs to Processor Options,
    a real search field of its own, not to OS."""
    if not text:
        return None
    m = _ANDROID_RE.search(text)
    if m:
        return f"Android {m.group(1)}"
    m = _LINUX_RE.search(text)
    if m:
        return m.group(1)
    m = _WINDOWS_RE.search(text)
    if m:
        return f"Windows {m.group(1)}"
    return None


# Checked in this order - GAC/SAC before LTSC/LTSB matters for a real row
# in the catalog: "Windows 11 IoT Enterprise GAC (64-bit) - Microsoft has
# not released Win 11 IoT Enterprise LTSC yet" mentions LTSC only to say
# it's *not* what this SKU is - checking LTSC first would misclassify it.
_EDITION_PATTERNS = [
    ("GAC", re.compile(r"\bGAC\b", re.IGNORECASE)),
    ("SAC", re.compile(r"\bSAC\b", re.IGNORECASE)),
    ("LTSC", re.compile(r"LTSC", re.IGNORECASE)),
    ("LTSB", re.compile(r"LTSB", re.IGNORECASE)),
    ("IoT Enterprise", re.compile(r"IoT\s*Enterprise", re.IGNORECASE)),
    ("Pro", re.compile(r"\bPro\b", re.IGNORECASE)),
]


def extract_os_edition(text):
    """'Windows 10 IoT Enterprise LTSC 64-Bit' -> 'LTSC'; 'Windows 11 Pro'
    -> 'Pro'; 'Android 12' -> None (no edition concept - only searchable
    by Version, same as an untagged storage description)."""
    if not text:
        return None
    for label, pat in _EDITION_PATTERNS:
        if pat.search(text):
            return label
    return None
