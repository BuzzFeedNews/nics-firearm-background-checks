#!/usr/bin/env python
import pandas as pd
import pdfplumber
import requests
import datetime
import re
from io import BytesIO

def parse_date(pdf):
    chars = pd.DataFrame(pdf.chars)
    updated_text = "".join(chars[
        (chars["fontname"] == "Times New Roman") &
        (chars["doctop"] < 175)
    ].sort_values(["doctop", "x0"])["text"])
    date_pat = r"UPDATED:\s+As of (.+)$"
    updated_date = re.search(date_pat, updated_text).group(1)
    d = datetime.datetime.strptime(updated_date, "%B %d, %Y")
    return d

if __name__ == "__main__":
    URL = "https://www.fbi.gov/about-us/cjis/nics/reports/active_records_in_the_nics-index.pdf"
    raw = requests.get(URL).content
    pdf = pdfplumber.load(BytesIO(raw))
    d = parse_date(pdf)
    print(d.strftime("%Y-%m"))
