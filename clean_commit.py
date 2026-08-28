import os
import pandas as pd
import numpy as np

# ======================================================
# Configuration
# ======================================================

DATA_DIR = r"E:\ai_pro_project"

INPUT_FILE = os.path.join(DATA_DIR, "commit_history_weekly.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "commit_summary.csv")

# ======================================================
# Load Dataset
# ======================================================

print("=" * 60)
print("Loading Commit History Dataset...")
print("=" * 60)

commit_df = pd.read_csv(INPUT_FILE)

print("\nDataset Shape :", commit_df.shape)

# ======================================================
# Missing Values
# ======================================================

print("\nMissing Values")

print(commit_df.isnull().sum())

# ======================================================
# Remove Duplicate Rows
# ======================================================

commit_df = commit_df.drop_duplicates()

print("\nDuplicate Rows Removed")

# ======================================================
# Standardize Tool Names
# ======================================================

commit_df["tool"] = (
    commit_df["tool"]
    .astype(str)
    .str.strip()
)

# ======================================================
# Convert Numeric Columns
# ======================================================

commit_df["week_index"] = pd.to_numeric(
    commit_df["week_index"],
    errors="coerce"
)

commit_df["commits"] = pd.to_numeric(
    commit_df["commits"],
    errors="coerce"
)

# ======================================================
# Remove Invalid Rows
# ======================================================

commit_df = commit_df.dropna(
    subset=["week_index", "commits"]
)

commit_df["week_index"] = commit_df["week_index"].astype(int)

commit_df["commits"] = commit_df["commits"].astype(int)

commit_df = commit_df[
    commit_df["commits"] >= 0
]

print("\nDataset cleaned successfully.")

# ======================================================
# Sort Data
# ======================================================

commit_df = commit_df.sort_values(
    ["tool", "week_index"]
)

# ======================================================
# Feature Engineering
# ======================================================

summary = []

for tool in commit_df["tool"].unique():

    temp = commit_df[
        commit_df["tool"] == tool
    ].sort_values("week_index")

    total_commits = temp["commits"].sum()

    avg_commits = round(
        temp["commits"].mean(),
        2
    )

    max_commits = temp["commits"].max()

    last30 = temp.tail(4)["commits"].sum()

    prev30 = temp.iloc[-8:-4]["commits"].sum()

    if prev30 == 0:
        growth = 0
    else:
        growth = round(
            ((last30 - prev30) / prev30) * 100,
            2
        )

    summary.append({

        "tool": tool,

        "total_commits_52w": total_commits,

        "avg_weekly_commits": avg_commits,

        "max_weekly_commits": max_commits,

        "commits_last_30d": last30,

        "commits_prev_30d": prev30,

        "commit_growth_pct": growth

    })

commit_summary = pd.DataFrame(summary)

# ======================================================
# Validation
# ======================================================

print("\nCommit Summary")

print(commit_summary.head())

print("\nRows :", commit_summary.shape[0])

print("Columns :", commit_summary.shape[1])

# ======================================================
# Export
# ======================================================

commit_summary.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n" + "=" * 60)
print("commit_summary.csv created successfully!")
print("Saved to:")
print(OUTPUT_FILE)
print("=" * 60)