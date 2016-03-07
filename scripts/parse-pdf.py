#!/usr/bin/env python
import pandas as pd
import datetime
import pdfplumber
from pdfplumber.utils import within_bbox, collate_chars
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

def parse_field(text):
    if text == None: return None
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
    if pd.isnull(x): return None
    return int(x.replace(",", ""))

def parse_page(page):

    month_crop = page.crop((0, 35, page.width, 65), strict=True)
    month_text = month_crop.extract_text(x_tolerance=2)
    month = parse_month(month_text)
    sys.stderr.write("\r" + month)

    table_crop = page.crop((0, 80, page.width, 485))
    _table = table_crop.extract_table(h="gutters",
        x_tolerance=5,
        y_tolerance=5,
        gutter_min_height=5)
    
    table = pd.DataFrame([ [ month ] + row for row in _table ])

    table.columns = COLUMNS
    table[table.columns[2:]] = table[table.columns[2:]].applymap(parse_value)

    table.loc[(table["state"] == "llinois"), "state"] = "Illinois"
    try: validate_data(table)
    except: raise Exception("Invalid data for " + month)

    return table

def parse_pdf(file_obj):
    pdf = pdfplumber.load(file_obj)

    checks = pd.concat(list(map(parse_page, pdf.pages)))\
        .reset_index(drop=True)

    return checks[checks["state"] != "Totals"]

if __name__ == "__main__":
    buf = getattr(sys.stdin, 'buffer', sys.stdin)
    checks = parse_pdf(buf)
    checks.to_csv(sys.stdout, index=False, float_format="%.0f")
    sys.stderr.write("\r\n")
