#!/usr/bin/env python
import pandas as pd
import datetime
import pdfplumber
from pdfplumber.utils import within_bbox, extract_text
from operator import itemgetter
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

def parse_month(month_str):
    d = datetime.datetime.strptime(month_str, "%B - %Y")
    return d.strftime("%Y-%m")

def validate_data(checks):
    try:
        assert(len(checks) > 0)
    except:
        raise Exception("No data found.")

    ## Test vertical totals
    # [2:] because first two columns are month and state name
    for c in COLUMNS[2:]:
        v_total = checks[c].iloc[-1]
        v_colsum = checks[c].sum()
        try:
            assert(v_colsum == (v_total * 2))
        except:
            raise Exception("Vertical totals don't match on {0}.".format(c))

    ## Test horizontal totals
    h_colsums = checks.fillna(0).sum(axis=1)
    h_totals = checks["totals"].fillna(0)
    zipped = zip(checks["state"], h_colsums, h_totals)
    for state, h_colsum, h_total in zipped:
        try:
            assert(h_colsum == (h_total * 2))
        except:
            raise Exception("Horizontal totals don't match on {0}.".format(state))

def parse_value(x):
    if pd.isnull(x) or x == "": return None
    return int(x.replace(",", ""))

def parse_page(page):
    month_chars = [ c for c in page.chars if c["non_stroking_color"] == (1, 0, 0) ]
    month_text = extract_text(month_chars, x_tolerance=2)
    month = parse_month(month_text)
    sys.stderr.write("\r" + month)

    table_crop = page.crop((
        0,
        [ w for w in page.extract_words() if w["text"] == "State" ][0]["bottom"],
        page.width,
        page.rects[-1]["bottom"],
    ))

    edge_xs = list(set(map(itemgetter("x0"), table_crop.edges)))
    leftmost_char = min(map(itemgetter("x0"), table_crop.chars)) 

    _table = table_crop.extract_table({
        "horizontal_strategy": "text",
        "vertical_strategy": "explicit",
        "explicit_vertical_lines": [ leftmost_char ] + edge_xs,
        "intersection_tolerance": 5,
        "text_y_tolerance": 0,
        "text_x_tolerance": 2,
    })

    table = pd.DataFrame([ [ month ] + row for row in _table ])

    table.columns = COLUMNS
    table[table.columns[2:]] = table[table.columns[2:]].applymap(parse_value)

    table.loc[(table["state"] == "llinois"), "state"] = "Illinois"
    table = table.loc[lambda df: df["state"].fillna("").str.strip() != ""]
    try: validate_data(table)
    except: raise Exception("Invalid data for " + month)

    return table

def parse_pdf(pdf):
    # Note: As of Nov. 2019 file, first page is documentation
    checks_gen = map(parse_page, pdf.pages[1:])
    checks = pd.concat(checks_gen).reset_index(drop=True)

    return checks[checks["state"] != "Totals"]

if __name__ == "__main__":
    with pdfplumber.open(sys.stdin.buffer) as pdf:
        checks = parse_pdf(pdf)

    checks.to_csv(sys.stdout, index=False, float_format="%.0f")

    sys.stderr.write("\r\n")
