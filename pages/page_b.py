import streamlit as st
import pandas as pd
import numpy as np
from utils.session_utils import get_current_df, set_df, log_transformation, get_transformation_log, undo_last_transformation
from utils.data_transformations import (
    get_missing_summary, drop_rows_with_missing, drop_columns_with_missing,
    fill_missing_constant, fill_missing_mean, fill_missing_median, fill_missing_mode,
    fill_missing_ffill, fill_missing_bfill,
    detect_duplicates, remove_duplicates,
    convert_to_numeric, convert_to_categorical, convert_to_datetime, clean_dirty_numeric,
    standardize_categorical, map_categorical_values, group_rare_categories, one_hot_encode,
    detect_outliers_iqr, detect_outliers_zscore, cap_outliers, remove_outlier_rows,
    min_max_scale, zscore_standardize,
    rename_columns, drop_columns, create_calculated_column, bin_numeric_column,
    validate_data, get_numeric_columns, get_categorical_columns
)


def show():
    st.markdown("""
    <div class="page-header">
        <div class="page-header-content">
            <h1 class="page-title">Cleaning & Preparation Studio</h1>
            <p class="page-subtitle">Transform and clean your data interactively</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    df = get_current_df()
    
    if df is None:
        st.warning("Please upload a dataset first on the Upload & Overview page.")
        return
    
    # Show transformation log sidebar
    col_main, col_sidebar = st.columns([3, 1])
    
    with col_sidebar:
        st.subheader("Transformation Log")
        log = get_transformation_log()
        if log:
            for entry in reversed(log):
                st.markdown(f"""
                <div style="font-size:11px; padding:4px 0; border-bottom:1px solid #333;">
                    <b>{entry['operation']}</b><br/>
                    <span style="color:#666;">{', '.join(entry['affected_columns'][:3])}{'...' if len(entry['affected_columns']) > 3 else ''}</span>
                </div>
                """, unsafe_allow_html=True)
            if st.button("Undo Last"):
                if undo_last_transformation():
                    st.success("Undone! Reloading...")
                    st.rerun()
        else:
            st.info("No transformations yet")
    
    with col_main:
        before_rows = len(df)
        
        tabs = st.tabs([
            "Missing Values", "Duplicates", "Data Types", "Categorical", 
            "Numeric/Outliers", "Scaling", "Columns", "Validation"
        ])
        
        with tabs[0]:
            st.subheader("Missing Values Handling")
            missing_summary = get_missing_summary(df)
            missing_cols = missing_summary[missing_summary['Missing Count'] > 0]['Column'].tolist()
            
            if missing_cols:
                st.dataframe(missing_summary[missing_summary['Missing Count'] > 0], use_container_width=True)
                
                mv_action = st.selectbox("Action", [
                    "Drop rows with missing values",
                    "Drop columns with >X% missing",
                    "Fill with constant value",
                    "Fill with mean (numeric only)",
                    "Fill with median (numeric only)",
                    "Fill with mode (most frequent)",
                    "Forward fill",
                    "Backward fill"
                ])
                
                if mv_action == "Drop rows with missing values":
                    selected_cols = st.multiselect("Columns to check", missing_cols)
                    if st.button("Apply"):
                        if selected_cols:
                            new_df = drop_rows_with_missing(df, selected_cols)
                            set_df(new_df)
                            log_transformation("Drop Missing Rows", {"columns": selected_cols}, selected_cols)
                            st.success(f"Removed {before_rows - len(new_df)} rows")
                            st.rerun()
                
                elif mv_action == "Drop columns with >X% missing":
                    threshold = st.slider("Threshold %", 0, 100, 50)
                    if st.button("Apply"):
                        new_df, dropped = drop_columns_with_missing(df, threshold)
                        if dropped:
                            set_df(new_df)
                            log_transformation("Drop Missing Columns", {"threshold": threshold}, dropped)
                            st.success(f"Dropped: {dropped}")
                            st.rerun()
                
                elif mv_action == "Fill with constant value":
                    selected_cols = st.multiselect("Columns", missing_cols)
                    fill_value = st.text_input("Value")
                    if st.button("Apply"):
                        if selected_cols:
                            try:
                                fill_val = float(fill_value) if '.' in fill_value else int(fill_value)
                            except:
                                fill_val = fill_value
                            new_df = fill_missing_constant(df, selected_cols, fill_val)
                            set_df(new_df)
                            log_transformation("Fill Constant", {"value": fill_value}, selected_cols)
                            st.success("Filled!")
                            st.rerun()
                
                elif mv_action == "Fill with mean (numeric only)":
                    numeric_missing = [c for c in missing_cols if pd.api.types.is_numeric_dtype(df[c])]
                    selected_cols = st.multiselect("Columns", numeric_missing)
                    if st.button("Apply"):
                        if selected_cols:
                            new_df = fill_missing_mean(df, selected_cols)
                            set_df(new_df)
                            log_transformation("Fill Mean", {}, selected_cols)
                            st.success("Filled!")
                            st.rerun()
                
                elif mv_action == "Fill with median (numeric only)":
                    numeric_missing = [c for c in missing_cols if pd.api.types.is_numeric_dtype(df[c])]
                    selected_cols = st.multiselect("Columns", numeric_missing)
                    if st.button("Apply"):
                        if selected_cols:
                            new_df = fill_missing_median(df, selected_cols)
                            set_df(new_df)
                            log_transformation("Fill Median", {}, selected_cols)
                            st.success("Filled!")
                            st.rerun()
                
                elif mv_action == "Fill with mode (most frequent)":
                    selected_cols = st.multiselect("Columns", missing_cols)
                    if st.button("Apply"):
                        if selected_cols:
                            new_df = fill_missing_mode(df, selected_cols)
                            set_df(new_df)
                            log_transformation("Fill Mode", {}, selected_cols)
                            st.success("Filled!")
                            st.rerun()
                
                elif mv_action == "Forward fill":
                    selected_cols = st.multiselect("Columns", missing_cols)
                    if st.button("Apply"):
                        if selected_cols:
                            new_df = fill_missing_ffill(df, selected_cols)
                            set_df(new_df)
                            log_transformation("Forward Fill", {}, selected_cols)
                            st.success("Applied!")
                            st.rerun()
                
                elif mv_action == "Backward fill":
                    selected_cols = st.multiselect("Columns", missing_cols)
                    if st.button("Apply"):
                        if selected_cols:
                            new_df = fill_missing_bfill(df, selected_cols)
                            set_df(new_df)
                            log_transformation("Backward Fill", {}, selected_cols)
                            st.success("Applied!")
                            st.rerun()
            else:
                st.success("No missing values!")
        
        with tabs[1]:
            st.subheader("Duplicate Handling")
            dupe_count = df.duplicated().sum()
            st.write(f"Full-row duplicates: {dupe_count}")
            
            if dupe_count > 0:
                with st.expander("View duplicates"):
                    dupes = detect_duplicates(df)
                    st.dataframe(dupes.head(50), use_container_width=True)
            
            subset_cols = st.multiselect("Subset columns (optional)", df.columns.tolist())
            keep_option = st.radio("Keep", ["first", "last", "none"], horizontal=True)
            
            if st.button("Remove Duplicates"):
                subset = subset_cols if subset_cols else None
                keep = None if keep_option == "none" else keep_option
                new_df = remove_duplicates(df, subset=subset, keep=keep)
                removed = before_rows - len(new_df)
                set_df(new_df)
                log_transformation("Remove Duplicates", {"subset": subset, "keep": keep}, subset_cols or list(df.columns))
                st.success(f"Removed {removed} duplicates")
                st.rerun()
        
        with tabs[2]:
            st.subheader("Data Type Conversion")
            
            dt_cols = st.multiselect("Columns", df.columns.tolist())
            dt_action = st.selectbox("Convert to", [
                "Numeric", "Categorical", "Datetime", "Clean dirty numeric ($, commas)"
            ])
            
            if st.button("Convert"):
                if dt_cols:
                    if dt_action == "Numeric":
                        new_df = convert_to_numeric(df, dt_cols)
                        set_df(new_df)
                        log_transformation("To Numeric", {}, dt_cols)
                    elif dt_action == "Categorical":
                        new_df = convert_to_categorical(df, dt_cols)
                        set_df(new_df)
                        log_transformation("To Categorical", {}, dt_cols)
                    elif dt_action == "Datetime":
                        date_fmt = st.text_input("Format (optional, e.g. %Y-%m-%d)")
                        new_df = convert_to_datetime(df, dt_cols, format=date_fmt or None)
                        set_df(new_df)
                        log_transformation("To Datetime", {"format": date_fmt}, dt_cols)
                    else:
                        new_df = clean_dirty_numeric(df, dt_cols)
                        set_df(new_df)
                        log_transformation("Clean Dirty Numeric", {}, dt_cols)
                    st.success(f"Converted {len(dt_cols)} columns")
                    st.rerun()
        
        with tabs[3]:
            st.subheader("Categorical Tools")
            cat_cols = get_categorical_columns(df)
            
            if cat_cols:
                cat_tabs = st.tabs(["Standardize", "Map", "Group Rare", "One-Hot"])
                
                with cat_tabs[0]:
                    std_cols = st.multiselect("Columns", cat_cols, key="std_cols")
                    std_op = st.selectbox("Operation", ["trim", "lower", "title", "trim_lower", "trim_title"])
                    if st.button("Standardize", key="std_btn"):
                        if std_cols:
                            new_df = standardize_categorical(df, std_cols, std_op)
                            set_df(new_df)
                            log_transformation(f"Standardize {std_op}", {}, std_cols)
                            st.success("Done!")
                            st.rerun()
                
                with cat_tabs[1]:
                    map_col = st.selectbox("Column", cat_cols, key="map_col")
                    mapping_text = st.text_area("Mapping (old=new, one per line)", "old1=new1\nold2=new2")
                    set_other = st.checkbox("Set unmapped to 'Other'")
                    if st.button("Apply Map", key="map_btn"):
                        mapping = {}
                        for line in mapping_text.strip().split('\n'):
                            if '=' in line:
                                k, v = line.split('=', 1)
                                mapping[k.strip()] = v.strip()
                        new_df = map_categorical_values(df, map_col, mapping, set_other)
                        set_df(new_df)
                        log_transformation("Map Values", {"mapping": mapping}, [map_col])
                        st.success("Done!")
                        st.rerun()
                
                with cat_tabs[2]:
                    rare_col = st.selectbox("Column", cat_cols, key="rare_col")
                    threshold = st.number_input("Min frequency", min_value=1, value=10)
                    if st.button("Group Rare", key="rare_btn"):
                        new_df = group_rare_categories(df, rare_col, threshold)
                        set_df(new_df)
                        log_transformation("Group Rare", {"threshold": threshold}, [rare_col])
                        st.success("Done!")
                        st.rerun()
                
                with cat_tabs[3]:
                    ohe_cols = st.multiselect("Columns", cat_cols, key="ohe_cols")
                    drop_first = st.checkbox("Drop first")
                    if st.button("Encode", key="ohe_btn"):
                        if ohe_cols:
                            new_df = one_hot_encode(df, ohe_cols, drop_first)
                            set_df(new_df)
                            log_transformation("One-Hot Encode", {"drop_first": drop_first}, ohe_cols)
                            st.success("Done!")
                            st.rerun()
            else:
                st.info("No categorical columns")
        
        with tabs[4]:
            st.subheader("Outlier Detection & Treatment")
            num_cols = get_numeric_columns(df)
            
            if num_cols:
                outlier_method = st.selectbox("Method", ["IQR (1.5*IQR)", "Z-score (threshold 3)"])
                selected_num = st.multiselect("Columns", num_cols, default=num_cols[:1])
                
                if selected_num and st.button("Detect"):
                    if outlier_method.startswith("IQR"):
                        outliers = detect_outliers_iqr(df, selected_num)
                    else:
                        outliers = detect_outliers_zscore(df, selected_num)
                    for col, info in outliers.items():
                        st.write(f"**{col}:** {info['count']} outliers")
                
                outlier_action = st.selectbox("Action", ["Cap/Winsorize", "Remove rows"])
                
                if st.button("Apply Treatment"):
                    if outlier_action == "Cap/Winsorize":
                        new_df, capped = cap_outliers(df, selected_num)
                        set_df(new_df)
                        log_transformation("Cap Outliers", {"method": outlier_method}, selected_num)
                    else:
                        new_df, removed = remove_outlier_rows(df, selected_num)
                        set_df(new_df)
                        log_transformation("Remove Outliers", {"method": outlier_method}, selected_num)
                        st.success(f"Removed {removed} rows")
                    st.rerun()
            else:
                st.info("No numeric columns")
        
        with tabs[5]:
            st.subheader("Scaling")
            num_cols = get_numeric_columns(df)
            
            if num_cols:
                scale_cols = st.multiselect("Columns to scale", num_cols, key="scale_cols")
                scale_method = st.selectbox("Method", ["Min-Max (0-1)", "Z-Score"])
                
                if st.button("Apply Scaling"):
                    if scale_cols:
                        if scale_method.startswith("Min-Max"):
                            new_df, params = min_max_scale(df, scale_cols)
                        else:
                            new_df, params = zscore_standardize(df, scale_cols)
                        set_df(new_df)
                        log_transformation(scale_method.split()[0] + " Scale", {}, scale_cols)
                        st.success("Done!")
                        st.rerun()
            else:
                st.info("No numeric columns")
        
        with tabs[6]:
            st.subheader("Column Operations")
            
            col_op = st.selectbox("Operation", ["Rename", "Drop", "Calculate", "Bin"])
            
            if col_op == "Rename":
                rename_map = {}
                for col in df.columns[:10]:
                    new_name = st.text_input(f"{col} →", col, key=f"rename_{col}")
                    if new_name != col:
                        rename_map[col] = new_name
                if st.button("Rename"):
                    if rename_map:
                        new_df = rename_columns(df, rename_map)
                        set_df(new_df)
                        log_transformation("Rename", rename_map, list(rename_map.keys()))
                        st.success("Done!")
                        st.rerun()
            
            elif col_op == "Drop":
                drop_cols = st.multiselect("Columns", df.columns.tolist(), key="drop_cols")
                if st.button("Drop"):
                    if drop_cols:
                        new_df = drop_columns(df, drop_cols)
                        set_df(new_df)
                        log_transformation("Drop Columns", {}, drop_cols)
                        st.success(f"Dropped {len(drop_cols)} columns")
                        st.rerun()
            
            elif col_op == "Calculate":
                new_name = st.text_input("New column name")
                formula = st.text_input("Formula (e.g., colA + colB)")
                if st.button("Create"):
                    if new_name and formula:
                        try:
                            new_df = create_calculated_column(df, new_name, formula)
                            set_df(new_df)
                            log_transformation("Create Column", {"formula": formula}, [new_name])
                            st.success("Created!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
            
            elif col_op == "Bin":
                bin_col = st.selectbox("Column", num_cols if 'num_cols' in dir() else [])
                n_bins = st.number_input("Bins", min_value=2, max_value=20, value=5)
                bin_method = st.selectbox("Method", ["Equal width", "Quantile"])
                new_bin_col = st.text_input("New name", f"{bin_col}_binned")
                if st.button("Bin"):
                    if bin_col and new_bin_col:
                        method = "equal_width" if bin_method == "Equal width" else "quantile"
                        new_df = bin_numeric_column(df, bin_col, new_bin_col, n_bins, method)
                        set_df(new_df)
                        log_transformation("Bin", {"bins": n_bins, "method": method}, [new_bin_col])
                        st.success("Done!")
                        st.rerun()
        
        with tabs[7]:
            st.subheader("Data Validation")
            
            # Initialize rules in session state if not present
            if 'validation_rules' not in st.session_state:
                st.session_state.validation_rules = []
            
            with st.expander("Range Check"):
                range_col = st.selectbox("Column", num_cols if 'num_cols' in dir() else [], key="val_range")
                range_min = st.number_input("Min", value=0.0, key="range_min")
                range_max = st.number_input("Max", value=100.0, key="range_max")
                if st.checkbox("Add range rule", key="chk_range"):
                    rule = {"type": "range", "column": range_col, "min": range_min, "max": range_max}
                    if rule not in st.session_state.validation_rules:
                        st.session_state.validation_rules.append(rule)
                        st.success(f"Added range rule for {range_col}")
            
            with st.expander("Category Check"):
                cat_col = st.selectbox("Column", cat_cols if 'cat_cols' in dir() else [], key="val_cat")
                allowed = st.text_input("Allowed (comma-separated)", "val1, val2", key="cat_allowed")
                if st.checkbox("Add category rule", key="chk_cat"):
                    rule = {"type": "category", "column": cat_col, "allowed": [v.strip() for v in allowed.split(",")]}
                    if rule not in st.session_state.validation_rules:
                        st.session_state.validation_rules.append(rule)
                        st.success(f"Added category rule for {cat_col}")
            
            with st.expander("Non-Null Check"):
                notnull_col = st.selectbox("Column", df.columns.tolist(), key="val_null")
                if st.checkbox("Add non-null rule", key="chk_null"):
                    rule = {"type": "non_null", "column": notnull_col}
                    if rule not in st.session_state.validation_rules:
                        st.session_state.validation_rules.append(rule)
                        st.success(f"Added non-null rule for {notnull_col}")
            
            # Display current rules
            if st.session_state.validation_rules:
                st.write("**Active Rules:**")
                for i, rule in enumerate(st.session_state.validation_rules):
                    cols = st.columns([4, 1])
                    with cols[0]:
                        st.write(f"{i+1}. {rule['type']}: {rule.get('column', 'N/A')}")
                    with cols[1]:
                        if st.button("Remove", key=f"del_rule_{i}"):
                            st.session_state.validation_rules.pop(i)
                            st.rerun()
            
            col_val1, col_val2 = st.columns([1, 1])
            with col_val1:
                if st.button("Validate", key="btn_validate"):
                    if st.session_state.validation_rules:
                        valid_df, violations = validate_data(df, st.session_state.validation_rules)
                        if violations.empty:
                            st.success("All records pass!")
                        else:
                            st.error(f"{len(violations)} violations")
                            st.dataframe(violations, use_container_width=True)
                    else:
                        st.info("No rules configured. Add rules above.")
            
            with col_val2:
                if st.button("Clear All Rules", key="btn_clear_rules"):
                    st.session_state.validation_rules = []
                    st.success("Rules cleared!")
                    st.rerun()
        after_rows = len(get_current_df())
        if after_rows != before_rows:
            st.info(f"Rows: {before_rows:,} → {after_rows:,} (Δ{after_rows - before_rows:+,})")