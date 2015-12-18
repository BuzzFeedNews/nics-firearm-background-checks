#!/usr/bin/env python
import pandas as pd
import datetime
import pdfplumber
import sys, os

COLUMNS = [
    "month",
    "state",
    "permit",
    "handgun",
    "long_gun",
    "other",
    "multiple",
    "admin",
    "prepawn_handgun",
    "prepawn_long_gun",
    "prepawn_other",
    "redemption_handgun",
    "redemption_long_gun",
    "redemption_other",
    "returned_handgun",
    "returned_long_gun",
    "returned_other",
    "rentals_handgun",
    "rentals_long_gun",
    "private_sale_handgun",
    "private_sale_long_gun",
    "private_sale_other",
    "return_to_seller_handgun",
    "return_to_seller_long_gun",
    "return_to_seller_other",
    "totals"
]

# Where, in pixels from the top,
# the data starts and ends on each page.
DATA_START_TOP = 80
DATA_END_TOP = 474

def get_between(chars, x0, x1):
    return chars[
        (chars["x0"] > x0) &
        (chars["x1"] < x1)
    ]

def parse_field(text):
    if text == "": return None
    if text[0] in "0123456789":
        return int(text.replace(",", ""))
    return text

def parse_month(month_str):
    d = datetime.datetime.strptime(month_str, "%B - %Y")
    return d.strftime("%Y-%m")

def parse_pdf(file_obj):
    pdf = pdfplumber.load(file_obj)
    rects = pd.DataFrame(pdf.rects)
    chars = pd.DataFrame(pdf.chars)

    # Find the leftmost side of the rectangles that appear on each page.
    rect_counts = rects["x0"].value_counts()
    edges = rect_counts[
        rect_counts == len(pdf.pages)
    ].sort_index().index

    # Use these edges to create boundaries, defining fields.
    bounds = list(zip(edges, edges[1:]))

    def parse_line(chars):
        fields = [ "".join(get_between(chars, x0, x1)["text"])
            for x0, x1 in bounds ]

        parsed = list(map(parse_field, fields))
        return parsed

    def parse_page_chars(chars):
        c = chars[
            (chars["top"] >= DATA_START_TOP) &
            (chars["top"] < DATA_END_TOP)
        ].sort_values([ "doctop", "x0" ])

        month = parse_month("".join(chars[
            (chars["size"] == 14.183) &
            (chars["top"] > 28)
        ]["text"]))

        data = c.groupby("doctop").apply(parse_line)
        return pd.DataFrame([ [ month ] + d for d in data ], columns=COLUMNS)


    checks = pd.concat([ parse_page_chars(chars[chars["pageid"] == p.pageid])
        for p in pdf.pages ]).reset_index(drop=True)

    assert(len(checks) > 0)
    assert((checks.fillna(0).sum(axis=1) != (checks["totals"] * 2)).sum() == 0)
    return checks

if __name__ == "__main__":
    buf = getattr(sys.stdin, 'buffer', sys.stdin)
    checks = parse_pdf(buf)
    checks.to_csv(sys.stdout, index=False, float_format="%.0f")
