#!/usr/bin/env python
import pandas as pd
import pdfplumber
import requests
import datetime
import re
from io import BytesIO

def parse_date(pdf):
    text = pdf.pages[0].extract_text(x_tolerance=5)
    date_pat = r"UPDATED:\s+As of (.+)\n"
    updated_date = re.search(date_pat, text).group(1)
    d = datetime.datetime.strptime(updated_date, "%B %d, %Y")
    return d

if __name__ == "__main__":
    URL = "https://www.fbi.gov/file-repository/active_records_in_the_nics-index.pdf"
    raw = requests.get(URL).content
    pdf = pdfplumber.load(BytesIO(raw))
    d = parse_date(pdf)
    print(d.strftime("%Y-%m"))
