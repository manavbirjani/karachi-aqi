
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Paths
FEATURES_FILE = "data/features_store.csv"
EDA_OUTPUT_DIR = "reports/eda"

# Ensure output dir exists
os.makedirs(EDA_OUTPUT_DIR, exist_ok=True)

def run_eda():
    # Load dataset
    if not os.path.exists(FEATURES_FILE):
        raise FileNotFoundError(f"{FEATURES_FILE} not found!")
    df = pd.read_csv(FEATURES_FILE)

    # If timestamp column exists, parse as datetime
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    print(f"Loaded dataset with {df.shape[0]} rows and {df.shape[1]} columns")

    # 1. Summary & Missing Values
    with open(os.path.join(EDA_OUTPUT_DIR, "summary.txt"), "w") as f:
        f.write(str(df.info()) + "\n\n")
        f.write("Missing Values:\n")
        f.write(str(df.isnull().sum()) + "\n\n")
        f.write("Describe:\n")
        f.write(str(df.describe()) + "\n\n")
    print("✅ Summary report saved.")

    # 2. Distribution of key pollutants
    pollutants = ["pm25", "pm10", "o3", "co", "no2", "so2"]
    for col in pollutants:
        if col in df.columns:
            plt.figure(figsize=(8, 5))
            sns.histplot(df[col], kde=True, bins=30, color="skyblue")
            plt.title(f"{col.upper()} Distribution")
            plt.xlabel(col.upper())
            plt.ylabel("Frequency")
            plt.tight_layout()
            plt.savefig(os.path.join(EDA_OUTPUT_DIR, f"{col}_distribution.png"))
            plt.close()
    print("✅ Distributions saved.")

    # 3. Correlation Heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(df.corr(), annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Feature Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(os.path.join(EDA_OUTPUT_DIR, "correlation_heatmap.png"))
    plt.close()
    print("✅ Correlation heatmap saved.")

    # 4. Change Rate Analysis
    if "pm25_change" in df.columns and "timestamp" in df.columns:
        plt.figure(figsize=(10, 5))
        sns.lineplot(data=df, x="timestamp", y="pm25_change", color="orange")
        plt.axhline(y=0, color="red", linestyle="--")
        plt.title("PM2.5 Change Rate Over Time")
        plt.tight_layout()
        plt.savefig(os.path.join(EDA_OUTPUT_DIR, "pm25_change_over_time.png"))
        plt.close()
        print("✅ PM2.5 change rate plot saved.")

    # 5. Outlier Detection
    for col in pollutants:
        if col in df.columns:
            plt.figure(figsize=(6, 4))
            sns.boxplot(x=df[col], color="lightgreen")
            plt.title(f"{col.upper()} Outlier Detection")
            plt.tight_layout()
            plt.savefig(os.path.join(EDA_OUTPUT_DIR, f"{col}_outliers.png"))
            plt.close()
    print("✅ Outlier boxplots saved.")

    print(f"\n📊 EDA completed. Reports saved in '{EDA_OUTPUT_DIR}' folder.")

if __name__ == "__main__":
    run_eda()
