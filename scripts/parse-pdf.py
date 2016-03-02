#!/usr/bin/env python
import pandas as pd
import datetime
import pdfplumber
import sys, os

COLUMNS = [
    "month",
    "state",
    "permit",
    "permit_recheck",
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

def validate_data(checks):
    try:
        assert(len(checks) > 0)
    except:
        raise Exception("No data found.")

    col_totals = checks.fillna(0).sum(axis=1)
    literal_totals = checks["totals"].fillna(0)
    try:
        assert((col_totals != (literal_totals * 2)).sum() == 0)
    except:
        msg = """Totals don't match
        col_totals: {0}
        literal_totals: {1}
        """.format(col_totals, literal_totals)
        raise Exception(msg)

def parse_pdf(file_obj):
    pdf = pdfplumber.load(file_obj)
    rects = pd.DataFrame(pdf.rects)
    chars = pd.DataFrame(pdf.chars)

    # Find the leftmost side of the rectangles that appear on each page.
    rect_counts = rects["x0"].value_counts()
    edges = rect_counts[
        rect_counts == len(pdf.pages)
    ].sort_index().index
    edges = ((pd.Series(edges) / 2).round() * 2).drop_duplicates()

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
        ]

        month = parse_month("".join(chars[
            (chars["size"] == 14.183) &
            (chars["top"] > 28)
        ]["text"]))

        data = c.groupby((c["doctop"] / 3).round()).apply(parse_line)
        df = pd.DataFrame([ [ month ] + d for d in data ], columns=COLUMNS)
        df.loc[(df["state"] == "llinois"), "state"] = "Illinois"
        try: validate_data(df)
        except: raise Exception("Invalid data for " + month)
        return df

    checks = pd.concat([ parse_page_chars(chars[chars["pageid"] == p.pageid])
        for p in pdf.pages ]).reset_index(drop=True)

    return checks

if __name__ == "__main__":
    buf = getattr(sys.stdin, 'buffer', sys.stdin)
    checks = parse_pdf(buf)
    checks.to_csv(sys.stdout, index=False, float_format="%.0f")
