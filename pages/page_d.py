import streamlit as st
import pandas as pd
import json
from datetime import datetime
from utils.session_utils import get_current_df, get_transformation_log, get_original_df


def show():
    st.markdown("""
    <div class="page-header">
        <div class="page-header-content">
            <h1 class="page-title">Export & Report</h1>
            <p class="page-subtitle">Export your cleaned data and transformation recipe</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    df = get_current_df()
    
    if df is None:
        st.warning("Please upload a dataset first on the Upload & Overview page.")
        return
    
    # Show current data stats
    original = get_original_df()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", f"{len(df):,}")
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        if original is not None:
            st.metric("Rows Changed", f"{len(df) - len(original):+,}")
    
    st.divider()
    
    # Export Dataset Section
    st.subheader("Export Dataset")
    
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="cleaned_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with export_col2:
        excel_buffer = pd.ExcelWriter("cleaned_data.xlsx", engine='openpyxl')
        df.to_excel(excel_buffer, index=False, sheet_name='Cleaned Data')
        excel_buffer.close()
        with open("cleaned_data.xlsx", "rb") as f:
            st.download_button(
                label="Download Excel",
                data=f,
                file_name="cleaned_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    st.divider()
    
    # Transformation Log Section
    st.subheader("Transformation Report")
    
    log = get_transformation_log()
    
    if log:
        # Create transformation report DataFrame
        report_data = []
        for i, entry in enumerate(log, 1):
            report_data.append({
                "Step": i,
                "Timestamp": entry['timestamp'][:19] if 'timestamp' in entry else "",
                "Operation": entry['operation'],
                "Affected Columns": ", ".join(entry['affected_columns'][:3]) + ("..." if len(entry['affected_columns']) > 3 else "")
            })
        
        report_df = pd.DataFrame(report_data)
        st.dataframe(report_df, use_container_width=True, hide_index=True)
        
        # Download transformation report as JSON
        json_report = json.dumps(log, indent=2)
        st.download_button(
            label="Download JSON Recipe",
            data=json_report,
            file_name="transformation_recipe.json",
            mime="application/json"
        )
        
        # Generate Python code
        st.subheader("Python Code Recipe")
        
        python_code = generate_python_code(log)
        st.code(python_code, language='python')
        
        st.download_button(
            label="Download Python Script",
            data=python_code,
            file_name="data_pipeline.py",
            mime="text/plain"
        )
    else:
        st.info("No transformations recorded yet. Go to the Cleaning & Preparation page to transform your data.")
    
    # Data summary report
    st.divider()
    st.subheader("Data Quality Report")
    
    if st.button("Generate Report"):
        report = {
            "generated_at": datetime.now().isoformat(),
            "dataset": {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "dtypes": {col: str(df[col].dtype) for col in df.columns}
            },
            "missing_values": {
                col: int(df[col].isnull().sum()) for col in df.columns if df[col].isnull().sum() > 0
            },
            "duplicates": int(df.duplicated().sum()),
            "transformations": len(log)
        }
        
        report_json = json.dumps(report, indent=2)
        st.json(report)
        
        st.download_button(
            label="Download Quality Report (JSON)",
            data=report_json,
            file_name="data_quality_report.json",
            mime="application/json"
        )


def generate_python_code(log):
    code_lines = [
        "# Auto-generated Data Cleaning Pipeline",
        "import pandas as pd",
        "import numpy as np",
        "",
        "# Load your dataset",
        "df = pd.read_csv('your_data.csv')  # Update path as needed",
        ""
    ]
    
    for entry in log:
        op = entry['operation']
        params = entry.get('parameters', {})
        cols = entry.get('affected_columns', [])
        
        if op in ["Data Load", "Load Sample"]:
            continue
            
        code_lines.append(f"# {op}")
        
        if op == "Drop Missing Rows":
            code_lines.append(f"df = df.dropna(subset={cols})")
        elif op == "Fill Constant":
            val = params.get('value', 0)
            for col in cols:
                code_lines.append(f"df['{col}'] = df['{col}'].fillna({val})")
        elif op == "Fill Mean":
            for col in cols:
                code_lines.append(f"df['{col}'] = df['{col}'].fillna(df['{col}'].mean())")
        elif op == "Fill Median":
            for col in cols:
                code_lines.append(f"df['{col}'] = df['{col}'].fillna(df['{col}'].median())")
        elif op == "Remove Duplicates":
            subset = params.get('subset')
            keep = params.get('keep', 'first')
            if subset:
                code_lines.append(f"df = df.drop_duplicates(subset={subset}, keep='{keep}')")
            else:
                code_lines.append(f"df = df.drop_duplicates(keep='{keep}')")
        elif op == "To Numeric":
            for col in cols:
                code_lines.append(f"df['{col}'] = pd.to_numeric(df['{col}'], errors='coerce')")
        elif op == "Drop Columns":
            code_lines.append(f"df = df.drop(columns={cols})")
        elif op == "Rename":
            code_lines.append(f"df = df.rename(columns={params})")
        elif "Scale" in op:
            for col in cols:
                if "Min-Max" in op:
                    code_lines.append(f"df['{col}'] = (df['{col}'] - df['{col}'].min()) / (df['{col}'].max() - df['{col}'].min())")
                else:
                    code_lines.append(f"df['{col}'] = (df['{col}'] - df['{col}'].mean()) / df['{col}'].std()")
        
        code_lines.append("")
    
    code_lines.extend([
        "# Save cleaned data",
        "df.to_csv('cleaned_output.csv', index=False)",
        "print(f'Saved {len(df)} rows to cleaned_output.csv')"
    ])
    
    return "\n".join(code_lines)