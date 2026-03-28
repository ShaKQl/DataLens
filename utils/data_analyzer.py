import pandas as pd


def get_numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return df.describe() for all numeric columns."""
    numeric_df = df.select_dtypes(include='number')
    if numeric_df.empty:
        return pd.DataFrame()
    return numeric_df.describe()


def get_categorical_summary(df: pd.DataFrame, categorical_cols: list) -> pd.DataFrame:
    """
    Return a summary DataFrame for categorical columns:
    unique count, mode, missing count.
    """
    rows = []
    for col in categorical_cols:
        series = df[col]
        unique_count = series.nunique(dropna=True)
        mode_vals = series.mode(dropna=True)
        mode = mode_vals.iloc[0] if not mode_vals.empty else "N/A"
        missing = int(series.isnull().sum())
        rows.append({
            "Column": col,
            "Unique Values": unique_count,
            "Mode": str(mode),
            "Missing Count": missing,
        })
    return pd.DataFrame(rows)


def get_missing_values_table(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame with missing count and missing percentage per column."""
    total = len(df)
    missing_count = df.isnull().sum()
    missing_pct = (missing_count / total * 100).round(2)
    result = pd.DataFrame({
        "Column": df.columns,
        "Missing Count": missing_count.values,
        "Missing %": missing_pct.values,
    })
    return result.sort_values("Missing Count", ascending=False).reset_index(drop=True)


def get_duplicates_count(df: pd.DataFrame) -> int:
    """Return the number of fully duplicate rows."""
    return int(df.duplicated().sum())
