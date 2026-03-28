import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils.session_utils import get_current_df
from utils.data_transformations import get_numeric_columns, get_categorical_columns


def show():
    st.markdown("""
    <div class="page-header">
        <div class="page-header-content">
            <h1 class="page-title">Visualization Builder</h1>
            <p class="page-subtitle">Create charts and explore your data visually</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    df = get_current_df()
    
    if df is None:
        st.warning("Please upload a dataset first on the Upload & Overview page.")
        return
    
    num_cols = get_numeric_columns(df)
    cat_cols = get_categorical_columns(df)
    all_cols = df.columns.tolist()
    
    # Chart configuration
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Chart Settings")
        
        chart_type = st.selectbox("Chart Type", [
            "Histogram", "Box Plot", "Scatter Plot", "Line Chart", "Bar Chart", "Heatmap"
        ])
        
        # X axis selection
        x_col = st.selectbox("X Axis", all_cols)
        
        # Y axis (not needed for histogram or heatmap)
        y_col = None
        if chart_type not in ["Histogram", "Heatmap"]:
            y_col = st.selectbox("Y Axis", [c for c in all_cols if c != x_col])
        
        # Color/grouping option
        color_col = st.selectbox("Color/Group (optional)", ["None"] + cat_cols)
        color_col = None if color_col == "None" else color_col
        
        # Aggregation for bar charts
        agg_func = None
        if chart_type == "Bar Chart":
            agg_func = st.selectbox("Aggregation", ["Count", "Sum", "Mean", "Median"])
        
        # Filtering options
        st.divider()
        st.write("**Filters**")
        
        filter_col = st.selectbox("Filter column", ["None"] + all_cols)
        if filter_col != "None":
            if df[filter_col].dtype == 'object' or df[filter_col].dtype.name == 'category':
                filter_vals = st.multiselect("Include values", df[filter_col].dropna().unique())
            else:
                min_val = float(df[filter_col].min())
                max_val = float(df[filter_col].max())
                filter_range = st.slider("Range", min_val, max_val, (min_val, max_val))
        
        # Top N for bar charts
        top_n = None
        if chart_type == "Bar Chart":
            top_n = st.number_input("Top N categories", min_value=0, max_value=50, value=0)
            if top_n == 0:
                top_n = None
    
    with col2:
        st.subheader("Chart Preview")
        
        # Apply filters
        chart_df = df.copy()
        if filter_col != "None":
            if df[filter_col].dtype == 'object' or df[filter_col].dtype.name == 'category':
                if filter_vals:
                    chart_df = chart_df[chart_df[filter_col].isin(filter_vals)]
            else:
                chart_df = chart_df[
                    (chart_df[filter_col] >= filter_range[0]) & 
                    (chart_df[filter_col] <= filter_range[1])
                ]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        try:
            if chart_type == "Histogram":
                if color_col:
                    for val in chart_df[color_col].dropna().unique()[:10]:
                        subset = chart_df[chart_df[color_col] == val][x_col].dropna()
                        if len(subset) > 0 and pd.api.types.is_numeric_dtype(chart_df[x_col]):
                            ax.hist(subset, alpha=0.6, label=str(val), bins=30)
                    ax.legend()
                else:
                    if pd.api.types.is_numeric_dtype(chart_df[x_col]):
                        ax.hist(chart_df[x_col].dropna(), bins=30, edgecolor='black')
                ax.set_xlabel(x_col)
                ax.set_ylabel("Frequency")
                ax.set_title(f"Histogram of {x_col}")
            
            elif chart_type == "Box Plot":
                if color_col:
                    groups = chart_df[color_col].dropna().unique()[:10]
                    data_to_plot = [chart_df[chart_df[color_col] == g][y_col].dropna() for g in groups]
                    ax.boxplot(data_to_plot, labels=groups)
                else:
                    ax.boxplot(chart_df[y_col].dropna())
                    ax.set_xticklabels([y_col])
                ax.set_ylabel(y_col)
                ax.set_title(f"Box Plot of {y_col}" + (f" by {color_col}" if color_col else ""))
            
            elif chart_type == "Scatter Plot":
                if color_col:
                    for val in chart_df[color_col].dropna().unique()[:10]:
                        subset = chart_df[chart_df[color_col] == val]
                        ax.scatter(subset[x_col], subset[y_col], alpha=0.6, label=str(val), s=20)
                    ax.legend()
                else:
                    ax.scatter(chart_df[x_col], chart_df[y_col], alpha=0.6, s=20)
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.set_title(f"Scatter: {y_col} vs {x_col}")
            
            elif chart_type == "Line Chart":
                # Sort by x if datetime or numeric
                if pd.api.types.is_datetime64_any_dtype(chart_df[x_col]) or pd.api.types.is_numeric_dtype(chart_df[x_col]):
                    chart_df = chart_df.sort_values(x_col)
                
                if color_col:
                    for val in chart_df[color_col].dropna().unique()[:10]:
                        subset = chart_df[chart_df[color_col] == val].groupby(x_col)[y_col].mean().reset_index()
                        ax.plot(subset[x_col], subset[y_col], marker='o', label=str(val), linewidth=2)
                    ax.legend()
                else:
                    grouped = chart_df.groupby(x_col)[y_col].mean().reset_index()
                    ax.plot(grouped[x_col], grouped[y_col], marker='o', linewidth=2)
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.set_title(f"Line Chart: {y_col} by {x_col}")
            
            elif chart_type == "Bar Chart":
                if agg_func == "Count":
                    grouped = chart_df[x_col].value_counts()
                elif agg_func == "Sum":
                    grouped = chart_df.groupby(x_col)[y_col].sum()
                elif agg_func == "Mean":
                    grouped = chart_df.groupby(x_col)[y_col].mean()
                else:  # Median
                    grouped = chart_df.groupby(x_col)[y_col].median()
                
                if top_n:
                    grouped = grouped.nlargest(top_n)
                
                grouped.head(20).plot(kind='bar', ax=ax)
                ax.set_xlabel(x_col)
                ax.set_ylabel(agg_func if agg_func else "Value")
                ax.set_title(f"Bar Chart: {agg_func} of {y_col if y_col else 'Count'} by {x_col}")
                plt.xticks(rotation=45, ha='right')
            
            elif chart_type == "Heatmap":
                # Correlation matrix of numeric columns
                numeric_df = chart_df.select_dtypes(include=[np.number])
                if len(numeric_df.columns) >= 2:
                    corr = numeric_df.corr()
                    im = ax.imshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
                    ax.set_xticks(range(len(corr.columns)))
                    ax.set_yticks(range(len(corr.columns)))
                    ax.set_xticklabels(corr.columns, rotation=45, ha='right')
                    ax.set_yticklabels(corr.columns)
                    plt.colorbar(im, ax=ax)
                    ax.set_title("Correlation Heatmap (Numeric Columns)")
                else:
                    ax.text(0.5, 0.5, "Need 2+ numeric columns", ha='center', va='center')
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # Download chart
            buf = plt.savefig('chart.png', bbox_inches='tight', dpi=150)
            with open('chart.png', 'rb') as f:
                st.download_button("Download Chart (PNG)", f, "chart.png", "image/png")
            
        except Exception as e:
            st.error(f"Chart error: {e}")
        finally:
            plt.close()
    
    # Quick chart gallery
    st.divider()
    st.subheader("Quick Gallery")
    
    if st.button("Generate Auto Charts"):
        if num_cols:
            cols = st.columns(2)
            
            with cols[0]:
                # Histogram of first numeric column
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.hist(df[num_cols[0]].dropna(), bins=30, edgecolor='black', color='steelblue')
                ax.set_title(f"Histogram: {num_cols[0]}")
                st.pyplot(fig)
                plt.close()
            
            with cols[1]:
                # Box plot if second numeric column exists
                if len(num_cols) > 1:
                    fig, ax = plt.subplots(figsize=(6, 4))
                    ax.boxplot([df[num_cols[0]].dropna(), df[num_cols[1]].dropna()], labels=[num_cols[0], num_cols[1]])
                    ax.set_title("Box Plot Comparison")
                    st.pyplot(fig)
                    plt.close()
            
            if cat_cols and num_cols:
                cols2 = st.columns(2)
                with cols2[0]:
                    # Bar chart
                    fig, ax = plt.subplots(figsize=(6, 4))
                    df[cat_cols[0]].value_counts().head(10).plot(kind='bar', ax=ax)
                    ax.set_title(f"Top {cat_cols[0]} Categories")
                    plt.xticks(rotation=45, ha='right')
                    st.pyplot(fig)
                    plt.close()
                
                with cols2[1]:
                    # Scatter if 2+ numeric columns
                    if len(num_cols) >= 2:
                        fig, ax = plt.subplots(figsize=(6, 4))
                        ax.scatter(df[num_cols[0]], df[num_cols[1]], alpha=0.5)
                        ax.set_xlabel(num_cols[0])
                        ax.set_ylabel(num_cols[1])
                        ax.set_title(f"Scatter: {num_cols[1]} vs {num_cols[0]}")
                        st.pyplot(fig)
                        plt.close()