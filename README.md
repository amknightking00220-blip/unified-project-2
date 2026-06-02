# unified-project-2
# Nassau Candy Logistics & Shipping Performance Analysis

## Overview

This project analyzes shipment and sales data from Nassau Candy Distributor to evaluate logistics performance, shipping efficiency, and regional delivery trends. The analysis focuses on shipping lead times, shipment volumes, and delivery performance across regions, states, and shipping modes.

## Objectives

- Calculate Shipping Lead Time (Ship Date − Order Date)
- Analyze shipment volume by region and state
- Identify high-volume regions with poor delivery performance
- Detect congestion-prone regions using lead time metrics
- Compare shipping efficiency between standard and expedited shipping
- Generate actionable business insights from logistics data

## Dataset

The dataset includes:

- Order ID
- Order Date
- Ship Date
- Ship Mode
- Customer Region
- Customer State
- Sales
- Units
- Gross Profit

## Key Metrics

### Shipping Lead Time
Number of days between Order Date and Ship Date.

### Shipment Volume
Total number of shipments handled by a region, state, or shipping mode.

### Average Lead Time
Average shipping lead time used to evaluate delivery speed.

### Lead Time Variability
Standard deviation of lead time used to measure delivery consistency.

## Analysis Performed

### Regional & State Performance
- Total shipments by region and state
- Total sales and units sold
- Average shipping lead time
- Comparison of high-volume regions

### Congestion Analysis
Identified regions and states with:
- High shipment volume
- High average lead time
- High lead time variability

### Shipping Mode Analysis
Compared:
- Standard Shipping
- Expedited Shipping

Metrics analyzed:
- Shipment count
- Average lead time
- Lead time variability
- Sales and profit contribution

## Tools Used

- Python
- Pandas
- NumPy
- Matplotlib
- Streamlit

## Key Insights

- Identified regions handling the highest shipment volumes.
- Detected regions with slower delivery performance.
- Compared efficiency across shipping methods.
- Highlighted areas that may require logistics optimization.

## Project Structure

```text
Nassau-Candy-Analysis/
├── data/
│   └── Nassau Candy Distributor.csv
├── dashboard/
│   └── nassau_candy_dashboard.py
├── README.md
```

## Author

Aditya Sharma

Data Analytics Project focused on Logistics, Supply Chain Analytics, and Business Intelligence.
