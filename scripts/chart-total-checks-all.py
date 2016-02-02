#!/usr/bin/env python
import pandas as pd
import seaborn as sb
import sys, os

checks = pd.read_csv(sys.stdin)

totals = checks.groupby("month")["totals"].sum()
tick_placement = pd.np.arange(2, len(totals), 12)

ax = totals.plot(kind="area", figsize=(12, 8), color="#000000", alpha=0.5)

ax.figure.set_facecolor("#FFFFFF")
ax.set_title("Monthly NICS Background Check Totals Since Nov. 1998", fontsize=24)
ax.set_yticklabels([ "{0:,.0f}".format(y) for y in ax.get_yticks() ], fontsize=12)
sb.plt.setp(ax.get_xticklabels(), rotation=0, fontsize=12)
ax.set_xticks(tick_placement)
ax.set_xticklabels([ totals.index[i].split("-")[0] for i in tick_placement ])
ax.set_xlabel("")
sb.plt.savefig(sys.stdout)
