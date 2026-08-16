"""
Ingest a Getac Select MSRP workbook into the normalized parts shape.

Structurally nothing like JLT/Winmate: one flat sheet, 5 columns (Model, SKU
ID, Description, MSRP, Currency), 371 rows. Each row is a complete, already
fixed pre-built SKU - Getac sells specific configurations, not a pick-one-
option-per-category matrix the way JLT/Winmate do. Decomposing a row's
description into independently-selectable category options would imply
combinations Getac doesn't actually sell, so every row becomes a single
"Base Unit:" record (code = SKU ID) rather than several per-category rows.

Since there's no separate CPU/OS column, this pulls a best-effort CPU and OS
value out of the free-text description into an `attributes` dict purely so
Search by Requirements has something to match against - these are NOT
selectable options, just search metadata on an otherwise fixed SKU.

Usage:
    python parse_getac.py <path-to-xlsx> [--out parts.json]
"""

import argparse
import json
import re
import sys
from pathlib import Path

import openpyxl

CPU_PATTERNS = [
    re.compile(r"(?:Intel|AMD)\s+.+?Processor", re.IGNORECASE),
    re.compile(r"Qualcomm\s+\S+", re.IGNORECASE),
]


def extract_cpu(description):
    if not description:
        return None
    for pat in CPU_PATTERNS:
        m = pat.search(description)
        if m:
            return m.group(0).strip()
    return None


def extract_os(description):
    if not description:
        return None
    m = re.search(r"Windows\s*11\s*(?:Pro|Professional)", description, re.IGNORECASE)
    if m:
        return "Windows 11 Pro"
    m = re.search(r"Android\s*\d+", description, re.IGNORECASE)
    if m:
        return m.group(0).strip()
    return None


def parse_workbook(path, brand="Getac"):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb[wb.sheetnames[0]]  # single-sheet workbook; sheet name has a stray encoding artifact

    header_cells = next(ws.iter_rows(min_row=1, max_row=1))
    headers = [str(c.value).strip() if c.value else None for c in header_cells]

    parts = []
    for values in ws.iter_rows(min_row=2, values_only=True):
        row = dict(zip(headers, values))
        model = row.get("Model")
        sku = row.get("SKU ID")
        description = row.get("Description")
        msrp = row.get("MSRP")
        if not (model and sku):
            continue

        description = str(description).strip() if description is not None else None
        attributes = {}
        cpu = extract_cpu(description)
        if cpu:
            attributes["cpu"] = cpu
        os_name = extract_os(description)
        if os_name:
            attributes["os"] = os_name

        parts.append({
            "brand": brand,
            "platform": str(model).strip(),
            "category": "Base Unit:",
            "code": str(sku).strip(),
            "description": description,
            "requires_review": False,  # manufacturer's own official catalog
            "Floor Price": None,
            "MSRP": msrp,
            "Cost": None,
            "Current Cost": None,
            "attributes": attributes,
        })

    return parts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx_path")
    ap.add_argument("--out", default=None, help="Output JSON path (default: alongside input, parts_<name>.json)")
    ap.add_argument("--brand", default="Getac", help="Vendor brand to tag every row with (default: Getac)")
    args = ap.parse_args()

    xlsx_path = Path(args.xlsx_path)
    parts = parse_workbook(xlsx_path, brand=args.brand)

    out_path = Path(args.out) if args.out else xlsx_path.with_name(f"parts_{xlsx_path.stem}.json")
    out_path.write_text(json.dumps(parts, indent=2), encoding="utf-8")

    by_platform = {}
    with_cpu = 0
    for p in parts:
        by_platform.setdefault(p["platform"], 0)
        by_platform[p["platform"]] += 1
        if p["attributes"].get("cpu"):
            with_cpu += 1

    print(f"Parsed {len(parts)} SKUs across {len(by_platform)} platforms ({with_cpu} with a detected CPU):")
    for platform, count in sorted(by_platform.items()):
        print(f"  {platform}: {count}")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    sys.exit(main())
