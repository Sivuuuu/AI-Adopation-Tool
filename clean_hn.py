import os
import pandas as pd
import numpy as np

# ======================================================
# Configuration
# ======================================================

DATA_DIR = r"E:\ai_pro_project"

INPUT_FILE = os.path.join(DATA_DIR, "hn_mentions_log.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "hn_clean.csv")

# ======================================================
# Load Dataset
# ======================================================

print("=" * 60)
print("Loading Hacker News Dataset...")
print("=" * 60)

hn_df = pd.read_csv(INPUT_FILE)

print("\nDataset Shape :", hn_df.shape)

# ======================================================
# Missing Values
# ======================================================

print("\nMissing Values")

print(hn_df.isnull().sum())

# ======================================================
# Remove Duplicate Rows
# ======================================================

hn_df = hn_df.drop_duplicates()

hn_df = hn_df.drop_duplicates(subset=["tool"])

print("\nDuplicate Rows Removed")

# ======================================================
# Standardize Tool Names
# ======================================================

hn_df["tool"] = (
    hn_df["tool"]
    .astype(str)
    .str.strip()
)

# ======================================================
# Convert Numeric Columns
# ======================================================

hn_df["hn_total_mentions"] = pd.to_numeric(
    hn_df["hn_total_mentions"],
    errors="coerce"
)

hn_df["hn_mentions_last_90d"] = pd.to_numeric(
    hn_df["hn_mentions_last_90d"],
    errors="coerce"
)

# ======================================================
# Handle Missing Values
# ======================================================

hn_df["hn_total_mentions"] = (
    hn_df["hn_total_mentions"]
    .fillna(0)
    .astype(int)
)

hn_df["hn_mentions_last_90d"] = (
    hn_df["hn_mentions_last_90d"]
    .fillna(0)
    .astype(int)
)

# ======================================================
# Validation
# ======================================================

print("\nFinal Missing Values")

print(hn_df.isnull().sum())

print("\nRows :", hn_df.shape[0])

print("Columns :", hn_df.shape[1])

print("\nData Types")

print(hn_df.dtypes)

# ======================================================
# Export
# ======================================================

hn_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n" + "=" * 60)

print("hn_clean.csv created successfully!")

print("Saved to")

print(OUTPUT_FILE)

print("=" * 60)

print("\nPreview")

print(hn_df.head())