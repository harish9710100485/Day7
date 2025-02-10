# Sales Data Prediction Script

## Overview

This Python script, developed by **Harish Myself (Intern Minweva)**, processes sales data from a TSV file, cleans it, and forecasts future sales quantities and item totals using **SARIMA** and **moving averages**. It also assigns random customer names and determines the sales quarter dynamically.

## Features

- Reads sales data from a TSV file
- Cleans and preprocesses data
- Converts USD to INR using exchange rates
- Uses **SARIMA** for time-series forecasting
- Fallbacks to moving averages when data is insufficient
- Assigns random customer names
- Determines the sales quarter dynamically
- Saves predictions to a TSV file

## Requirements

Ensure you have the following Python libraries installed:

```sh
pip install pandas numpy statsmodels pmdarima
```

## How to Use

1. **Update the file path** to your TSV sales data in `file_path`.
2. Run the script:

```sh
python sales_forecast.py
```

3. The predictions will be saved in:
   ```sh
   C:\Users\haris\Desktop\Day8\predictions_with_dynamic_quarter.tsv
   ```

## File Structure

```sh
📂 Project Folder
├── sales_forecast.py   # Main script
├── Sales_Data_for_Analysis.tsv   # Input data file (update path)
├── predictions_with_dynamic_quarter.tsv   # Output file
└── README.md   # This file
```

## Expected Output Format

The output TSV file contains the following columns:

| PART NO | year | Predicted Quantity | Predicted Item Total | Currency | Customer Name | Quarter |
| ------- | ---- | ------------------ | -------------------- | -------- | ------------- | ------- |
| ABC123  | 2025 | 150                | 25000                | INR      | CustomerA     | Q1      |
| XYZ456  | 2025 | 200                | 32000                | INR      | CustomerB     | Q2      |

## Troubleshooting

- If you get a **FileNotFoundError**, check and update `file_path`.
- If all historical data is zero, predictions will be set to zero.
- If SARIMA fails, the script falls back to a **moving average** approach.

## License

This project is open-source. Feel free to modify and improve it!

Author : Harish

Intern : Minervasoft

