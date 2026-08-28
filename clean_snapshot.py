import os
import pandas as pd
import numpy as np

# ======================================================
# Configuration
# ======================================================

DATA_DIR = r"E:\ai_pro_project"

INPUT_FILE = os.path.join(DATA_DIR, "snapshot_log.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "snapshot_clean.csv")

# ======================================================
# Load Dataset
# ======================================================

print("=" * 50)
print("Loading Snapshot Dataset...")
print("=" * 50)

snapshot_df = pd.read_csv(INPUT_FILE)

print("\nDataset Shape :", snapshot_df.shape)

# ======================================================
# Missing Values
# ======================================================

print("\nMissing Values")

print(snapshot_df.isnull().sum())

# ======================================================
# Remove Duplicate Rows
# ======================================================

snapshot_df = snapshot_df.drop_duplicates()

snapshot_df = snapshot_df.drop_duplicates(subset=["tool"])

print("\nDuplicate Rows Removed")

# ======================================================
# Standardize Text Columns
# ======================================================

snapshot_df["tool"] = (
    snapshot_df["tool"]
    .astype(str)
    .str.strip()
)

snapshot_df["repo"] = (
    snapshot_df["repo"]
    .astype(str)
    .str.strip()
)

snapshot_df["pypi_package"] = (
    snapshot_df["pypi_package"]
    .astype(str)
    .str.strip()
)

# ======================================================
# Handle Missing Package Names
# ======================================================

snapshot_df["pypi_package"] = (
    snapshot_df["pypi_package"]
    .replace("nan", np.nan)
    .replace("", np.nan)
    .fillna("N/A")
)

# ======================================================
# Numeric Columns
# ======================================================

numeric_columns = [

    "github_stars",

    "github_forks",

    "github_open_issues",

    "pypi_last_month_downloads",

    "stackoverflow_question_count"

]

for col in numeric_columns:

    snapshot_df[col] = pd.to_numeric(

        snapshot_df[col],

        errors="coerce"

    )

    snapshot_df[col] = snapshot_df[col].fillna(0)

# ======================================================
# Data Types
# ======================================================

snapshot_df["github_stars"] = snapshot_df["github_stars"].astype(int)

snapshot_df["github_forks"] = snapshot_df["github_forks"].astype(int)

snapshot_df["github_open_issues"] = snapshot_df["github_open_issues"].astype(int)

snapshot_df["stackoverflow_question_count"] = (
    snapshot_df["stackoverflow_question_count"]
    .astype(int)
)

snapshot_df["pypi_last_month_downloads"] = (
    snapshot_df["pypi_last_month_downloads"]
    .astype(int)
)

# ======================================================
# Final Validation
# ======================================================

print("\nFinal Missing Values")

print(snapshot_df.isnull().sum())

print("\nFinal Shape")

print(snapshot_df.shape)

print("\nData Types")

print(snapshot_df.dtypes)

# ======================================================
# Export
# ======================================================

snapshot_df.to_csv(

    OUTPUT_FILE,

    index=False

)

print("\n" + "=" * 50)

print("snapshot_clean.csv created successfully!")

print("Saved to")

print(OUTPUT_FILE)

print("=" * 50)

print("\nPreview")

print(snapshot_df.head())