#!/usr/bin/env python
import sys, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
from matplotlib.dates import MonthLocator
import seaborn as sb
sb.set()

checks = (
    pd.read_csv(sys.stdin)
    .assign(
        month_dt = lambda df: pd.to_datetime(df["month"], format = "%Y-%m")
    )
)

checks["year_int"] = checks["month"].apply(lambda x: int(x.split("-")[0]))
checks["month_int"] = checks["month"].apply(lambda x: int(x.split("-")[1]))

latest_month_count = (
    checks
    .iloc[0]
    .pipe(lambda x: x["month_int"] + (x["year_int"] * 12))
)

totals = (
    checks
    .loc[lambda df: (df["month_int"] + (df["year_int"] * 12)) 
        > (latest_month_count - 12*3)]
    .groupby("month_dt")
    ["totals"]
    .sum()
)

ax = totals.plot(kind="area", figsize=(12, 8), color="#000000", alpha=0.5)
ax.figure.set_facecolor("#FFFFFF")
ax.set_title(
    "NICS Background Check Totals — Past 36 Months",
    fontsize=24
)

plt.setp(ax.get_yticklabels(), fontsize=12)
ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

ax.xaxis.set_minor_locator(MonthLocator(range(1, 13)))
ax.set_xlabel("")

plt.savefig(sys.stdout.buffer)
