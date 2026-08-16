# 🌫️ Karachi AQI Prediction System

An end-to-end Python Machine Learning and Data Engineering pipeline designed to predict, forecast, and monitor the Air Quality Index (AQI) of Karachi using real-time atmospheric data.

🚀 **Live Dashboard:** [Deploy on Streamlit Community Cloud]

---

## 📊 Features

*   **Real-Time Data Fetching:** Seamless integration with the World Air Quality Index (WAQI) API to pull live pollution metrics (PM2.5, PM10, CO, NO2, SO2, O3).
*   **Predictive ML Model:** A Random Forest Regressor trained on historical datasets to calculate today's AQI and forecast trends.
*   **Interactive Dashboard:** Streamlit dashboard utilizing Plotly to visualize daily predictions and 3-day future trends.
*   **Pipeline Automation:** Configured GitHub Actions workflows to schedule automated daily data collection and model runs.

---

## 🛠️ Tech Stack

*   **Language:** Python 3.11
*   **Libraries:** Pandas, NumPy, Scikit-Learn, Joblib, Plotly, Streamlit
*   **API Integration:** REST API (WAQI)
*   **DevOps/CI/CD:** GitHub Actions

---

## ⚙️ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/manavbirjani/karachi-aqi.git
cd karachi-aqi
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory:
```env
AQI_API_TOKEN=your_waqi_api_token
```

### 3. Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run the Pipeline
*   **Train the model:**
    ```bash
    python train_model.py
    ```
*   **Generate today's predictions:**
    ```bash
    python predict_today.py
    ```
*   **Launch the Streamlit Dashboard:**
    ```bash
    streamlit run app.py
    ```

---

## ☁️ Deployment Guide (Streamlit Community Cloud)

1. Log into [Streamlit Share](https://share.streamlit.io/) with your GitHub account.
2. Click **Create App** and select this repository.
3. Set the Main File Path to `app.py`.
4. Under **Advanced Settings > Secrets**, paste your API token:
   ```toml
   AQI_API_TOKEN = "your_actual_token"
   ```
5. Click **Deploy!**