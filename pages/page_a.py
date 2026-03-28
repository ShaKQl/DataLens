import streamlit as st
import pandas as pd
from utils.data_loader import load_data
from utils.data_analyzer import (
    get_numeric_summary,
    get_categorical_summary,
    get_missing_values_table,
    get_duplicates_count,
)
from utils.session_utils import reset_session, get_current_df, set_df, log_transformation


def show():
    st.markdown("""
    <div class="page-header">
        <div class="page-header-content">
            <h1 class="page-title">Upload & Overview</h1>
            <p class="page-subtitle">Upload your dataset and explore its structure</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df = get_current_df()

    # File uploader with dynamic key for reset
    uploader_key = f"file_uploader_{st.session_state.get('reset_counter', 0)}"
    st.markdown(
        '<p class="uploader-label">Upload CSV, Excel, or JSON file</p>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        "Upload data file",
        type=["csv", "xlsx", "xls", "json"],
        key=uploader_key,
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        if st.session_state.get('uploaded_file_name') != uploaded_file.name:
            with st.spinner("Loading data..."):
                loaded_df = load_data(uploaded_file)
            if loaded_df is not None:
                set_df(loaded_df, store_original=True)
                st.session_state['uploaded_file_name'] = uploaded_file.name
                df = loaded_df
                st.success(f"Loaded: {uploaded_file.name} ({len(loaded_df):,} rows, {len(loaded_df.columns)} columns)")
                log_transformation("Data Load", {"filename": uploaded_file.name}, list(loaded_df.columns))
            else:
                st.error("Failed to load file. Check format.")
                return

    if df is None:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">◈</div>
            <p class="empty-title">No data loaded</p>
            <p class="empty-sub">Upload a CSV, Excel, or JSON file to begin</p>
        </div>
        """, unsafe_allow_html=True)

        # Sample data options
        st.markdown("<p class='uploader-label'>Or use sample data:</p>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load E-commerce Sample", use_container_width=True):
                try:
                    sample_df = pd.read_csv("sample_data/ecommerce_sales.csv")
                    set_df(sample_df, store_original=True)
                    st.session_state['uploaded_file_name'] = "ecommerce_sales.csv (sample)"
                    log_transformation("Load Sample", {"filename": "ecommerce_sales.csv"}, list(sample_df.columns))
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not load sample: {e}")
        with col2:
            if st.button("Load HR Employees Sample", use_container_width=True):
                try:
                    sample_df = pd.read_csv("sample_data/hr_employees.csv")
                    set_df(sample_df, store_original=True)
                    st.session_state['uploaded_file_name'] = "hr_employees.csv (sample)"
                    log_transformation("Load Sample", {"filename": "hr_employees.csv"}, list(sample_df.columns))
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not load sample: {e}")
        return

    # Stats strip
    n_rows, n_cols = df.shape
    missing_total = int(df.isnull().sum().sum())
    dupes = get_duplicates_count(df)

    st.markdown(f"""
    <div class="stats-strip">
        <div class="stat-pill">
            <span class="stat-num">{n_rows:,}</span>
            <span class="stat-lbl">Rows</span>
        </div>
        <div class="stat-pill">
            <span class="stat-num">{n_cols}</span>
            <span class="stat-lbl">Columns</span>
        </div>
        <div class="stat-pill">
            <span class="stat-num">{missing_total:,}</span>
            <span class="stat-lbl">Missing Values</span>
        </div>
        <div class="stat-pill">
            <span class="stat-num">{dupes:,}</span>
            <span class="stat-lbl">Duplicate Rows</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tabs for different views
    tab_overview, tab_columns, tab_numeric, tab_categorical, tab_missing = st.tabs([
        "Overview", "Columns", "Numeric", "Categorical", "Missing Values"
    ])

    with tab_overview:
        st.subheader("Dataset Preview")
        st.dataframe(df.head(100), use_container_width=True, height=300)

        st.subheader("Data Types Summary")
        type_counts = df.dtypes.value_counts()
        cols = st.columns(min(len(type_counts), 4))
        for i, (dtype, count) in enumerate(type_counts.items()):
            with cols[i % len(cols)]:
                st.metric(str(dtype), count)

    with tab_columns:
        col_df = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str),
            "Non-Null Count": df.count().values,
            "Null Count": df.isnull().sum().values,
            "Unique Values": [df[c].nunique() for c in df.columns],
        })
        st.dataframe(col_df, use_container_width=True, hide_index=True)

    with tab_numeric:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            num_summary = get_numeric_summary(df)
            st.dataframe(num_summary.style.format("{:.2f}"), use_container_width=True)
        else:
            st.info("No numeric columns found.")

    with tab_categorical:
        cat_cols = df.select_dtypes(exclude=['number']).columns.tolist()
        if cat_cols:
            cat_summary = get_categorical_summary(df, cat_cols)
            st.dataframe(cat_summary, use_container_width=True, hide_index=True)
        else:
            st.info("No categorical columns found.")

    with tab_missing:
        mv_table = get_missing_values_table(df)
        mv_display = mv_table[mv_table["Missing Count"] > 0]
        if not mv_display.empty:
            st.dataframe(mv_display, use_container_width=True, hide_index=True)
            st.subheader("Missing Values by Column")
            st.bar_chart(mv_display.set_index('Column')['Missing Count'])
        else:
            st.success("No missing values found!")

    # Reset button
    st.markdown('<div class="reset-zone">', unsafe_allow_html=True)
    if st.button("Reset Session", key="reset_btn"):
        reset_session()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)