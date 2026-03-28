import pandas as pd
import streamlit as st


def load_csv(file) -> "pd.DataFrame | None":
    """Load a CSV file into a DataFrame."""
    encodings = ["utf-8", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            if hasattr(file, 'seek'):
                file.seek(0)
            return pd.read_csv(file, encoding=enc)
        except UnicodeDecodeError:
            continue
        except Exception as e:
            st.error(f"CSV parse error: {e}")
            return None
    st.error("Could not decode the CSV file. Try saving it as UTF-8.")
    return None


def load_excel(file) -> "pd.DataFrame | None":
    """Load an Excel file into a DataFrame."""
    try:
        return pd.read_excel(file)
    except Exception as e:
        st.error(f"Excel parse error: {e}")
        return None


def load_json(file) -> "pd.DataFrame | None":
    """Load a JSON file into a DataFrame."""
    try:
        if hasattr(file, 'seek'):
            file.seek(0)
        return pd.read_json(file)
    except ValueError:
        try:
            import json
            if hasattr(file, 'seek'):
                file.seek(0)
            data = json.load(file)
            return pd.json_normalize(data)
        except Exception as e:
            st.error(f"JSON parse error: {e}")
            return None
    except Exception as e:
        st.error(f"JSON load error: {e}")
        return None


def _dispatch(source, name: str) -> "pd.DataFrame | None":
    """Route a file-like object to the right loader by extension."""
    n = name.lower()
    if n.endswith(".csv"):
        return load_csv(source)
    elif n.endswith((".xlsx", ".xls")):
        return load_excel(source)
    elif n.endswith(".json"):
        return load_json(source)
    else:
        st.error("Unsupported file type. Please upload a CSV, Excel, or JSON file.")
        return None


def load_data(uploaded_file) -> "pd.DataFrame | None":
    """Load a DataFrame from a Streamlit UploadedFile."""
    if uploaded_file is None:
        return None

    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > 200:
        st.warning(f"File is {size_mb:.1f} MB. Large files may load slowly.")

    return _dispatch(uploaded_file, uploaded_file.name)