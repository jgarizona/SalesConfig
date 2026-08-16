"""
Ingest a CipherLab price-list workbook into the normalized parts shape.

Single real data sheet ("One Page" - the other tabs in the real file are
empty placeholders). Flat rows, no category column: "Model Code" combines a
product-family prefix (e.g. "1000A", "RS38") with a coarse type suffix
("Product" / "Accessory" / "Adapter" / "Software") - e.g. "1000A Product",
"1023 Accessory". That suffix is the closest thing CipherLab's data has to a
category, mapped through category_map.py the same way Winmate's raw labels
are.

Unlike Getac, there is no CPU spec anywhere in this data - most of the
catalog (scanners, readers, adapters) has no CPU concept at all, and even
the Android-based mobile-computer families (RK/RS series) only mention
Android version + RAM, never a chipset. Storing a fabricated CPU value would
be inventing data the vendor never published, so this only extracts OS/RAM
as search attributes where the description actually states them.

Usage:
    python parse_cipherlab.py <path-to-xlsx> [--out parts.json]
"""

import argparse
import json
import re
import sys
from pathlib import Path

import openpyxl

from category_map import to_canonical

DATA_SHEET = "One Page"


def extract_os(description):
    if not description:
        return None
    m = re.search(r"Android\s*\d+", description, re.IGNORECASE)
    return m.group(0).strip() if m else None


def extract_ram(description):
    if not description:
        return None
    m = re.search(r"(\d+\s*GB?)\s*RAM", description, re.IGNORECASE)
    return m.group(1).replace(" ", "").upper() if m else None


def split_model_code(model_code):
    """'1000A Product' -> ('1000A', 'Product'). Some real rows have a third
    middle token ('8200 Service Advantage') - platform is always just the
    first token and category is always just the last, so a family's
    warranty/service SKUs still group under the same platform as its
    products/accessories rather than fragmenting into a separate '8200
    Service' platform bucket Sales would never show next to plain '8200'."""
    tokens = model_code.split()
    if not tokens:
        return model_code.strip(), model_code.strip()
    platform = tokens[0]
    category = tokens[-1] if len(tokens) > 1 else tokens[0]
    return platform, category


def parse_workbook(path, brand="CipherLab"):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb[DATA_SHEET]

    header_row = None
    headers = {}
    for r in range(1, 10):
        row_vals = {c: ws.cell(row=r, column=c).value for c in range(1, 20)}
        if any(v and str(v).strip() == "Model Code" for v in row_vals.values()):
            header_row = r
            for c, v in row_vals.items():
                if v:
                    headers[str(v).strip()] = c
            break
    if header_row is None:
        raise ValueError(f"Could not find the 'Model Code' header row in {DATA_SHEET!r}")

    col_model = headers.get("Model Code")
    col_product = headers.get("Product Code")
    col_desc = headers.get("Description")
    col_price = headers.get("List Price (USD)")

    parts = []
    for r in range(header_row + 1, ws.max_row + 1):
        model_code = ws.cell(row=r, column=col_model).value if col_model else None
        product_code = ws.cell(row=r, column=col_product).value if col_product else None
        description = ws.cell(row=r, column=col_desc).value if col_desc else None
        price = ws.cell(row=r, column=col_price).value if col_price else None

        if not (model_code and product_code):
            continue

        platform, raw_category = split_model_code(str(model_code))
        description = str(description).strip() if description is not None else None

        attributes = {}
        os_name = extract_os(description)
        if os_name:
            attributes["os"] = os_name
        ram = extract_ram(description)
        if ram:
            attributes["ram"] = ram

        parts.append({
            "brand": brand,
            "platform": platform,
            "category": to_canonical(raw_category),
            "code": str(product_code).strip(),
            "description": description,
            "requires_review": False,  # manufacturer's own official catalog
            "Floor Price": None,
            "MSRP": price,
            "Cost": None,
            "Current Cost": None,
            "attributes": attributes,
        })

    return parts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx_path")
    ap.add_argument("--out", default=None, help="Output JSON path (default: alongside input, parts_<name>.json)")
    ap.add_argument("--brand", default="CipherLab", help="Vendor brand to tag every row with (default: CipherLab)")
    args = ap.parse_args()

    xlsx_path = Path(args.xlsx_path)
    parts = parse_workbook(xlsx_path, brand=args.brand)

    out_path = Path(args.out) if args.out else xlsx_path.with_name(f"parts_{xlsx_path.stem}.json")
    out_path.write_text(json.dumps(parts, indent=2), encoding="utf-8")

    by_platform = {}
    for p in parts:
        by_platform.setdefault(p["platform"], 0)
        by_platform[p["platform"]] += 1

    print(f"Parsed {len(parts)} rows across {len(by_platform)} product families:")
    for platform, count in sorted(by_platform.items()):
        print(f"  {platform}: {count}")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    sys.exit(main())
