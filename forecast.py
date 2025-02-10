import pandas as pd
import numpy as np
import warnings
import csv
from statsmodels.tsa.statespace.sarimax import SARIMAX
import random

warnings.filterwarnings("ignore")

# Load Data
file_path = r"C:\Users\haris\Desktop\Day8\Sales_Data_for_Analysis.tsv"  # **Update with actual path**

try:
    df = pd.read_csv(file_path, sep="\t")
except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
    exit()

# Data Cleaning and Preprocessing
df.columns = df.columns.str.strip()
df.rename(columns={
    "PERIOD": "year", "QTY": "Quantity", "TOTAL PRICE (INR)": "Item Total",
    "CURRENCY": "Currency", "EX RATE": "Exchange Rate"
}, inplace=True)

required_columns = ["year", "Currency", "Item Total", "Exchange Rate"]
for col in required_columns:
    if col not in df.columns:
        print(f"Error: Column '{col}' not found in the dataset!")
        exit()

df["year"] = pd.to_datetime(df["year"], errors="coerce", dayfirst=True).dt.year
df.dropna(subset=["year"], inplace=True)
df["year"] = df["year"].astype(int)

df["Currency"] = df["Currency"].str.strip().str.upper()

if "Exchange Rate" in df.columns:
    df.loc[df["Currency"] == "USD", "Item Total"] *= df["Exchange Rate"]
    df["Currency"] = "INR"
else:
    print("Warning: 'Exchange Rate' column not found, using default rate.")
    df.loc[df["Currency"] == "USD", "Item Total"] *= 75  # Default exchange rate
    df["Currency"] = "INR"

if df.empty:
    print("No valid data available. Exiting.")
    exit()

latest_year = int(df["year"].max())

# Group Data
grouped = df.groupby(["PART NO", "year"])[["Quantity", "Item Total"]].sum().reset_index()

predictions = []
customer_names = ["CustomerA", "CustomerB", "CustomerC", "CustomerD", "CustomerE"]  # List of example customer names

# Function to calculate quarter based on the month
def get_quarter(month):
    if 1 <= month <= 3:
        return "Q1"
    elif 4 <= month <= 6:
        return "Q2"
    elif 7 <= month <= 9:
        return "Q3"
    else:
        return "Q4"

for part_no in grouped["PART NO"].unique():
    part_data = grouped[grouped["PART NO"] == part_no].copy()
    part_data.set_index("year", inplace=True)  # Set year as index for time series

    # Check if all historical data is zero
    if part_data["Quantity"].sum() == 0 and part_data["Item Total"].sum() == 0:
        print(f"All zero historical data for {part_no}, predicting zero.")
        predictions.append([part_no, latest_year + 1, 0, 0, "INR", random.choice(customer_names), "Q1"])
        continue

    # If not enough data, use simple moving average
    if len(part_data) < 3:
        print(f"Not enough data for SARIMA on {part_no}, using Moving Average.")
        pred_quantity = int(round(part_data["Quantity"].rolling(window=2).mean().iloc[-1] if len(part_data) > 1 else part_data["Quantity"].mean()))
        pred_total = int(round(part_data["Item Total"].rolling(window=2).mean().iloc[-1] if len(part_data) > 1 else part_data["Item Total"].mean()))
        predictions.append([part_no, latest_year + 1, max(0, pred_quantity), max(0, pred_total), "INR", random.choice(customer_names), "Q1"])
        continue

    try:
        # Auto-tune SARIMA parameters
        auto_model_qty = auto_arima(part_data["Quantity"], seasonal=True, suppress_warnings=True, trace=False)
        auto_model_total = auto_arima(part_data["Item Total"], seasonal=True, suppress_warnings=True, trace=False)

        # Fit SARIMA for Quantity
        model_quantity = SARIMAX(part_data["Quantity"], order=auto_model_qty.order, seasonal_order=auto_model_qty.seasonal_order,
                                 enforce_stationarity=False, enforce_invertibility=False)
        results_quantity = model_quantity.fit()
        pred_quantity = int(max(0, round(results_quantity.get_forecast(steps=1).predicted_mean.iloc[0])))

        # Fit SARIMA for Item Total
        model_total = SARIMAX(part_data["Item Total"], order=auto_model_total.order, seasonal_order=auto_model_total.seasonal_order,
                              enforce_stationarity=False, enforce_invertibility=False)
        results_total = model_total.fit()
        pred_total = int(max(0, round(results_total.get_forecast(steps=1).predicted_mean.iloc[0])))

    except Exception as e:
        print(f"Error in SARIMA for {part_no}: {e}")
        pred_quantity = max(0, int(round(part_data["Quantity"].mean())))
        pred_total = max(0, int(round(part_data["Item Total"].mean())))

    # Determine the quarter dynamically based on the month (for this example, using current year prediction)
    prediction_month = 12  # We assume the prediction is in December
    quarter = get_quarter(prediction_month)

    # Append the predicted values along with customer name and dynamic quarter
    predictions.append([part_no, latest_year + 1, pred_quantity, pred_total, "INR", random.choice(customer_names), quarter])

# Check if predictions list has the expected number of columns
print(f"Number of columns in predictions list: {len(predictions[0])}")
print(f"Number of rows in predictions list: {len(predictions)}")

# Convert to DataFrame
predictions_df = pd.DataFrame(predictions, columns=["PART NO", "year", "Predicted Quantity", "Predicted Item Total", "Currency", "Customer Name", "Quarter"])

# Save Output
output_file = r"C:\Users\haris\Desktop\Day8\predictions_with_dynamic_quarter.tsv"  # **Update path**
predictions_df.to_csv(output_file, index=False, sep="\t", quoting=csv.QUOTE_NONNUMERIC)

print(f"Predictions saved at: {output_file}")
print(predictions_df)
