#!/usr/bin/env python
import sys, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
sb.set()

checks = pd.read_csv(sys.stdin)

checks["year_int"] = checks["month"].apply(lambda x: int(x.split("-")[0]))
checks["month_int"] = checks["month"].apply(lambda x: int(x.split("-")[1]))

latest_month_count = checks.iloc[0]["month_int"] + (checks.iloc[0]["year_int"] * 12)

totals = checks[
    (checks["month_int"] + (checks["year_int"] * 12)) > (latest_month_count - 12*3)
].groupby("month")["totals"].sum()
tick_placement = np.arange(len(totals) - 1, 0, -3)

ax = totals.plot(kind="area", figsize=(12, 8), color="#000000", alpha=0.5)
ax.figure.set_facecolor("#FFFFFF")
ax.set_title("NICS Background Check Totals — Past 36 Months", fontsize=24)
ax.set_yticklabels([ "{0:,.0f}".format(y) for y in ax.get_yticks() ], fontsize=12)
ax.set_xticks(tick_placement)
ax.set_xticklabels([ totals.index[i] for i in tick_placement ])
ax.set_xlim(0, len(totals) - 1)
plt.setp(ax.get_xticklabels(), rotation=0, fontsize=12)
ax.set_xlabel("")

plt.savefig(sys.stdout.buffer)
