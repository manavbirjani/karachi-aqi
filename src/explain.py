

import os
import joblib
import glob
import pandas as pd

# Fixed: match current model file name exactly
MODEL_GLOB = "models/karachi_aqi_model.pkl"
FEATURES = "data/features_store.csv"
OUT_DIR = "reports"

def get_latest_model():
    files = sorted(glob.glob(MODEL_GLOB))
    if not files:
        raise FileNotFoundError("No model found.")
    return files[-1]

def main():
    try:
        import shap
        import matplotlib.pyplot as plt
    except Exception:
        raise SystemExit("Install shap and matplotlib: pip install shap matplotlib")

    if not os.path.exists(FEATURES):
        raise FileNotFoundError(f"{FEATURES} not found. Run build_features.py first.")

    model = joblib.load(get_latest_model())
    df = pd.read_csv(FEATURES)
    # choose a sample set for background
    X = df.drop(columns=["timestamp"], errors="ignore").fillna(0)
    # safe: if target column present, drop it
    for c in ["aqi", "predicted_aqi"]:
        if c in X.columns:
            X = X.drop(columns=[c])

    explainer = shap.Explainer(model, X)
    # explain last row
    x_to_explain = X.iloc[-1:, :]
    shap_values = explainer(x_to_explain)

    os.makedirs(OUT_DIR, exist_ok=True)
    # summary plot (uses small sample if X large)
    shap.summary_plot(shap_values, x_to_explain, show=False)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "shap_summary.png"))
    print("Saved SHAP summary to reports/shap_summary.png")

    # save raw shap values and feature importance
    sv = shap_values.values
    feat_names = x_to_explain.columns.tolist()
    df_sv = pd.DataFrame(sv, columns=feat_names)
    df_sv.to_csv(os.path.join(OUT_DIR, "shap_values.csv"), index=False)
    print("Saved shap_values.csv")

if __name__ == "__main__":
    main()
