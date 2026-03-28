"""Data transformation utilities for the Data Wrangling app."""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple


def get_missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return missing value summary per column."""
    total = len(df)
    missing = df.isnull().sum()
    pct = (missing / total * 100).round(2)
    return pd.DataFrame({
        'Column': df.columns,
        'Missing Count': missing.values,
        'Missing %': pct.values
    }).sort_values('Missing Count', ascending=False)


def drop_rows_with_missing(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Drop rows with missing values in specified columns."""
    return df.dropna(subset=columns)


def drop_columns_with_missing(df: pd.DataFrame, threshold_pct: float) -> pd.DataFrame:
    """Drop columns with missing values above threshold percentage."""
    missing_pct = df.isnull().mean() * 100
    cols_to_drop = missing_pct[missing_pct > threshold_pct].index.tolist()
    return df.drop(columns=cols_to_drop), cols_to_drop


def fill_missing_constant(df: pd.DataFrame, columns: List[str], value: Any) -> pd.DataFrame:
    """Fill missing values with a constant."""
    df = df.copy()
    for col in columns:
        df[col] = df[col].fillna(value)
    return df


def fill_missing_mean(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Fill missing values with column mean."""
    df = df.copy()
    for col in columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].mean())
    return df


def fill_missing_median(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Fill missing values with column median."""
    df = df.copy()
    for col in columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())
    return df


def fill_missing_mode(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Fill missing values with column mode (most frequent)."""
    df = df.copy()
    for col in columns:
        mode_val = df[col].mode()
        if not mode_val.empty:
            df[col] = df[col].fillna(mode_val.iloc[0])
    return df


def fill_missing_ffill(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Forward fill missing values."""
    df = df.copy()
    for col in columns:
        df[col] = df[col].ffill()
    return df


def fill_missing_bfill(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Backward fill missing values."""
    df = df.copy()
    for col in columns:
        df[col] = df[col].bfill()
    return df


def detect_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
    """Return duplicate rows."""
    if subset:
        return df[df.duplicated(subset=subset, keep=False)]
    return df[df.duplicated(keep=False)]


def remove_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None, keep: str = 'first') -> pd.DataFrame:
    """Remove duplicate rows."""
    return df.drop_duplicates(subset=subset, keep=keep)


def convert_to_numeric(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Convert columns to numeric, coercing errors."""
    df = df.copy()
    for col in columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def convert_to_categorical(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Convert columns to categorical."""
    df = df.copy()
    for col in columns:
        df[col] = df[col].astype('category')
    return df


def convert_to_datetime(df: pd.DataFrame, columns: List[str], format: Optional[str] = None) -> pd.DataFrame:
    """Convert columns to datetime."""
    df = df.copy()
    for col in columns:
        df[col] = pd.to_datetime(df[col], format=format, errors='coerce')
    return df


def clean_dirty_numeric(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Clean dirty numeric strings (remove $, £, commas)."""
    df = df.copy()
    for col in columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(r'[$£,€\s]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def standardize_categorical(df: pd.DataFrame, columns: List[str], operation: str = 'trim_lower') -> pd.DataFrame:
    """Standardize categorical values."""
    df = df.copy()
    for col in columns:
        if df[col].dtype == object or pd.api.types.is_categorical_dtype(df[col]):
            if operation == 'trim':
                df[col] = df[col].astype(str).str.strip()
            elif operation == 'lower':
                df[col] = df[col].astype(str).str.lower()
            elif operation == 'title':
                df[col] = df[col].astype(str).str.title()
            elif operation == 'trim_lower':
                df[col] = df[col].astype(str).str.strip().str.lower()
            elif operation == 'trim_title':
                df[col] = df[col].astype(str).str.strip().str.title()
    return df


def map_categorical_values(df: pd.DataFrame, column: str, mapping: Dict[str, str], set_other: bool = False) -> pd.DataFrame:
    """Map/replace categorical values using a dictionary."""
    df = df.copy()
    if set_other:
        unique_vals = set(df[column].dropna().unique())
        mapped_vals = set(mapping.keys())
        other_vals = unique_vals - mapped_vals
        full_mapping = mapping.copy()
        for val in other_vals:
            full_mapping[val] = 'Other'
        df[column] = df[column].map(full_mapping).fillna(df[column])
    else:
        df[column] = df[column].map(mapping).fillna(df[column])
    return df


def group_rare_categories(df: pd.DataFrame, column: str, threshold: int, other_label: str = 'Other') -> pd.DataFrame:
    """Group rare categories below frequency threshold into 'Other'."""
    df = df.copy()
    value_counts = df[column].value_counts()
    rare_categories = value_counts[value_counts < threshold].index.tolist()
    df[column] = df[column].replace(rare_categories, other_label)
    return df


def one_hot_encode(df: pd.DataFrame, columns: List[str], drop_first: bool = False) -> pd.DataFrame:
    """One-hot encode categorical columns."""
    return pd.get_dummies(df, columns=columns, drop_first=drop_first)


def detect_outliers_iqr(df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
    """Detect outliers using IQR method."""
    outlier_info = {}
    for col in columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            outlier_info[col] = {
                'count': len(outliers),
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'indices': outliers.index.tolist()
            }
    return outlier_info


def detect_outliers_zscore(df: pd.DataFrame, columns: List[str], threshold: float = 3.0) -> Dict[str, Any]:
    """Detect outliers using Z-score method."""
    outlier_info = {}
    for col in columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            outliers = df[z_scores > threshold]
            outlier_info[col] = {
                'count': len(outliers),
                'threshold': threshold,
                'indices': df[z_scores > threshold].index.tolist()
            }
    return outlier_info


def cap_outliers(df: pd.DataFrame, columns: List[str], method: str = 'iqr') -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Cap/winsorize outliers at specified quantiles."""
    df = df.copy()
    capped_counts = {}
    for col in columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
            else:  # quantile
                lower = df[col].quantile(0.05)
                upper = df[col].quantile(0.95)
            
            count_before = ((df[col] < lower) | (df[col] > upper)).sum()
            df[col] = df[col].clip(lower, upper)
            capped_counts[col] = int(count_before)
    return df, capped_counts


def remove_outlier_rows(df: pd.DataFrame, columns: List[str], method: str = 'iqr') -> Tuple[pd.DataFrame, int]:
    """Remove rows containing outliers."""
    outlier_mask = pd.Series([False] * len(df), index=df.index)
    for col in columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
            else:
                mean = df[col].mean()
                std = df[col].std()
                lower = mean - 3 * std
                upper = mean + 3 * std
            outlier_mask |= (df[col] < lower) | (df[col] > upper)
    
    rows_removed = outlier_mask.sum()
    return df[~outlier_mask], int(rows_removed)


def min_max_scale(df: pd.DataFrame, columns: List[str]) -> Tuple[pd.DataFrame, Dict[str, Tuple[float, float]]]:
    """Apply min-max scaling to numeric columns."""
    df = df.copy()
    scaling_params = {}
    for col in columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            min_val = df[col].min()
            max_val = df[col].max()
            if max_val != min_val:
                df[col] = (df[col] - min_val) / (max_val - min_val)
                scaling_params[col] = (float(min_val), float(max_val))
    return df, scaling_params


def zscore_standardize(df: pd.DataFrame, columns: List[str]) -> Tuple[pd.DataFrame, Dict[str, Tuple[float, float]]]:
    """Apply z-score standardization to numeric columns."""
    df = df.copy()
    scaling_params = {}
    for col in columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            mean = df[col].mean()
            std = df[col].std()
            if std != 0:
                df[col] = (df[col] - mean) / std
                scaling_params[col] = (float(mean), float(std))
    return df, scaling_params


def rename_columns(df: pd.DataFrame, rename_map: Dict[str, str]) -> pd.DataFrame:
    """Rename columns using a mapping dictionary."""
    return df.rename(columns=rename_map)


def drop_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Drop specified columns."""
    return df.drop(columns=columns)


def create_calculated_column(df: pd.DataFrame, new_col: str, formula: str) -> pd.DataFrame:
    """Create a new column using a formula string."""
    df = df.copy()
    try:
        # Safer evaluation using only column references
        df[new_col] = df.eval(formula, engine='python')
    except Exception as e:
        raise ValueError(f"Error evaluating formula '{formula}': {e}")
    return df


def bin_numeric_column(df: pd.DataFrame, column: str, new_col: str, n_bins: int, method: str = 'equal_width') -> pd.DataFrame:
    """Bin numeric column into categories."""
    df = df.copy()
    if method == 'equal_width':
        df[new_col] = pd.cut(df[column], bins=n_bins, labels=[f'Bin_{i+1}' for i in range(n_bins)])
    elif method == 'quantile':
        df[new_col] = pd.qcut(df[column], q=n_bins, labels=[f'Q_{i+1}' for i in range(n_bins)], duplicates='drop')
    return df


def validate_data(df: pd.DataFrame, rules: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Validate data against rules.
    Returns (valid_rows, violations_table).
    """
    violations = []
    valid_mask = pd.Series([True] * len(df), index=df.index)
    
    for rule in rules:
        rule_type = rule.get('type')
        column = rule.get('column')
        
        if rule_type == 'range':
            min_val = rule.get('min')
            max_val = rule.get('max')
            if min_val is not None:
                mask = df[column] >= min_val
                violations.extend([
                    {'row': idx, 'column': column, 'rule': f'>= {min_val}', 'value': val}
                    for idx, val in df[~mask][column].items()
                ])
                valid_mask &= mask
            if max_val is not None:
                mask = df[column] <= max_val
                violations.extend([
                    {'row': idx, 'column': column, 'rule': f'<= {max_val}', 'value': val}
                    for idx, val in df[~mask][column].items()
                ])
                valid_mask &= mask
                
        elif rule_type == 'category':
            allowed = rule.get('allowed', [])
            mask = df[column].isin(allowed) | df[column].isna()
            violations.extend([
                {'row': idx, 'column': column, 'rule': f'in {allowed}', 'value': val}
                for idx, val in df[~mask][column].items()
            ])
            valid_mask &= mask
            
        elif rule_type == 'non_null':
            mask = df[column].notna()
            violations.extend([
                {'row': idx, 'column': column, 'rule': 'non-null', 'value': None}
                for idx in df[~mask].index
            ])
            valid_mask &= mask
    
    violations_df = pd.DataFrame(violations)
    return df[valid_mask], violations_df


def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    """Return list of numeric column names."""
    return df.select_dtypes(include=[np.number]).columns.tolist()


def get_categorical_columns(df: pd.DataFrame) -> List[str]:
    """Return list of categorical/object column names."""
    return df.select_dtypes(include=['object', 'category']).columns.tolist()


def get_datetime_columns(df: pd.DataFrame) -> List[str]:
    """Return list of datetime column names."""
    return df.select_dtypes(include=['datetime64']).columns.tolist()
