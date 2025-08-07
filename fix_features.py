import pandas as pd

# Load the original CSV file
df = pd.read_csv("data/features.csv")

# Convert 'event_timestamp' to datetime and localize to UTC
df["event_timestamp"] = pd.to_datetime(df["event_timestamp"]).dt.tz_localize("UTC")

# Add 'created' column same as 'event_timestamp'
df["created"] = df["event_timestamp"]

# Save as proper parquet file
df.to_parquet("data/features.parquet", index=False)

print("✅ Successfully fixed and saved features.parquet")
