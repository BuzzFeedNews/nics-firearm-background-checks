#!/usr/bin/env python
import sys, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import seaborn as sb
sb.set()

checks = (
    pd.read_csv(sys.stdin)
    .assign(
        month_dt = lambda df: pd.to_datetime(df["month"], format = "%Y-%m")
    )
)

totals = checks.groupby("month_dt")["totals"].sum()

ax = totals.plot(kind="area", figsize=(12, 8), color="#000000", alpha=0.5)

ax.figure.set_facecolor("#FFFFFF")
ax.set_title(
    "Monthly NICS Background Check Totals Since Nov. 1998",
    fontsize=24
)

plt.setp(ax.get_yticklabels(), fontsize=12)
ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

ax.set_xlabel("")

plt.savefig(sys.stdout.buffer)
