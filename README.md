# AI Data Wrangler & Visualizer

A comprehensive Streamlit application for data wrangling and visualization, built for the Data Wrangling and Visualization (5COSC038C) coursework.

## Features

### Page A — Upload & Overview
- Upload CSV, Excel (xlsx/xls), and JSON files
- Load sample datasets (E-commerce and HR Employees)
- View dataset statistics (rows, columns, missing values, duplicates)
- Explore data with tabs: Overview, Columns, Numeric, Categorical, Missing Values
- Data preview with first 100 rows
- Missing values visualization

### Page B — Cleaning & Preparation Studio
- **Missing Values**: Drop rows/columns, fill with constant/mean/median/mode/forward/backward
- **Duplicates**: Detect and remove duplicates by subset or full row
- **Data Types**: Convert to numeric, categorical, datetime; clean dirty numeric strings
- **Categorical**: Standardize (trim, lower, title), map values, group rare categories, one-hot encode
- **Numeric/Outliers**: Detect using IQR or Z-score, cap/winsorize or remove
- **Scaling**: Min-Max (0-1) and Z-Score standardization
- **Column Operations**: Rename, drop, create calculated columns, bin numeric columns
- **Validation**: Range checks, category checks, non-null checks
- **Transformation Log**: Track all changes with undo functionality

### Page C — Visualization Builder
- **6 Chart Types**: Histogram, Box Plot, Scatter Plot, Line Chart, Bar Chart, Heatmap
- **Customization**: X/Y axis selection, color/grouping, aggregation (count/sum/mean/median)
- **Filtering**: By category or numeric range
- **Top N**: Limit bar charts to top N categories
- **Auto Gallery**: Generate quick charts automatically
- **Export**: Download charts as PNG

### Page D — Export & Report
- Export cleaned data as CSV or Excel
- View transformation log with timestamps
- Download JSON recipe of all transformations
- Generate Python code that replays the pipeline
- Data quality report with statistics

### Additional Features
- **Dark/Light Theme Toggle**: Persistent across pages
- **Session-Based Navigation**: No new tabs, smooth transitions
- **Session State Management**: Data persists across page switches
- **Sample Datasets**: Two pre-built datasets for demonstration

## Installation

```bash
# Clone or navigate to the project directory
cd "files (66)"

# Install dependencies
pip install -r requirements.txt
```

## Running the App

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Sample Data

Two sample datasets are included in the `sample_data/` folder:
1. **ecommerce_sales.csv**: 1500+ rows, 11 columns with order data, customer info, prices, categories
2. **hr_employees.csv**: 1200+ rows, 14 columns with employee HR data, salaries, performance

Both datasets include:
- Mixed data types (numeric, categorical, datetime)
- Missing values for testing imputation
- Duplicate rows for testing deduplication
- Dirty numeric data (currency symbols) for testing cleaning

## Project Structure

```
.
├── app.py                      # Main entry point
├── requirements.txt            # Python dependencies
├── sample_data/                # Sample datasets
│   ├── ecommerce_sales.csv
│   └── hr_employees.csv
├── pages/                      # Page modules
│   ├── page_a.py              # Upload & Overview
│   ├── page_b.py              # Cleaning & Preparation
│   ├── page_c.py              # Visualization Builder
│   └── page_d.py              # Export & Report
├── utils/                      # Utility modules
│   ├── session_utils.py        # Session state & theme
│   ├── data_loader.py          # File loading
│   ├── data_analyzer.py        # Data profiling
│   └── data_transformations.py # All transformation functions
└── assets/
    └── style.css               # Custom styling with dark/light theme
```

## Dependencies

- streamlit >= 1.28.0
- pandas >= 2.0.0
- numpy >= 1.24.0
- matplotlib >= 3.7.0
- openpyxl >= 3.1.0
- scikit-learn >= 1.3.0

## Requirements Satisfied

### Core Functionality (60 points)
- ✅ Upload + overview profiling with tabs
- ✅ Missing values tools (8 different methods)
- ✅ Categorical tools + mapping UI
- ✅ Scaling/normalization + numeric cleaning
- ✅ Visualization builder with 6 chart types
- ✅ Export + transformation report

### Engineering Quality (25 points)
- ✅ Clean code structure (functions/modules)
- ✅ Session state + caching
- ✅ Error handling + validations
- ✅ Usability: clear UI, helpful instructions

### Bonus Features (up to +20)
- ✅ Undo feature + recipe replay (Python script)
- Session persistence for repeatability

## Deployment

The app can be deployed to Streamlit Community Cloud:

1. Push code to GitHub
2. Connect repository at [share.streamlit.io](https://share.streamlit.io)
3. App will be publicly accessible

## Authors

Group project for 5COSC038C Data Wrangling and Visualization
