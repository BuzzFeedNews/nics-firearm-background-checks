#!/usr/bin/env python
import sys, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
sb.set()

checks = pd.read_csv(sys.stdin)

totals = checks.groupby("month")["totals"].sum()
tick_placement = np.arange(2, len(totals), 12)

ax = totals.plot(kind="area", figsize=(12, 8), color="#000000", alpha=0.5)

ax.figure.set_facecolor("#FFFFFF")
ax.set_title("Monthly NICS Background Check Totals Since Nov. 1998", fontsize=24)
ax.set_yticklabels([ "{0:,.0f}".format(y) for y in ax.get_yticks() ], fontsize=12)
plt.setp(ax.get_xticklabels(), rotation=0, fontsize=12)
ax.set_xticks(tick_placement)
ax.set_xticklabels([ totals.index[i].split("-")[0] for i in tick_placement ])
ax.set_xlim(0, len(totals) - 1)
ax.set_xlabel("")

plt.savefig(sys.stdout.buffer)
