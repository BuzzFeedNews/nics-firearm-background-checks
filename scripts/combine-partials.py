from pathlib import Path

import pandas as pd

csv_paths = Path("data/partial/").glob("*.csv")
(
    pd.concat((pd.read_csv(path, dtype=str) for path in csv_paths))
    .drop_duplicates(subset=["month", "state"])
    .to_csv("data/nics-firearm-background-checks.csv", index=False)
)
