# convert_to_parquet.py

import pandas as pd

# Load CSV
df = pd.read_csv("feature_store/feature_repo/data/features.csv")

# Save as Parquet
df.to_parquet("feature_store/feature_repo/data/features.parquet", index=False)

print("✅ Converted features.csv to features.parquet successfully.")
