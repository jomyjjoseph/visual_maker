import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Smart Data Cleaner", page_icon="🧹", layout="wide")
st.title("🧹 Smart Data Cleaner for Power BI")

uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"], accept_multiple_files=False)

def safe_read_csv(fileobj):
    # Try utf-8, then latin1 fallback
    try:
        return pd.read_csv(fileobj, encoding="utf-8")
    except Exception:
        fileobj.seek(0)
        return pd.read_csv(fileobj, encoding="latin1")

def infer_and_convert_dates(df):
    for col in df.columns:
        # only attempt on object columns to avoid converting numeric columns wrongly
        if df[col].dtype == "object":
            try:
                converted = pd.to_datetime(df[col], errors="coerce", dayfirst=False)
                # if a reasonable fraction parses to datetime, keep the conversion
                if converted.notna().sum() / max(1, len(converted)) > 0.3:
                    df[col] = converted
            except Exception:
                pass
    return df

def smart_fill(df):
    for col in df.columns:
        if df[col].isnull().sum() == 0:
            continue

        if pd.api.types.is_numeric_dtype(df[col]):
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            # fill with mode if available, else leave as-is (or choose min)
            try:
                mode_val = df[col].mode(dropna=True)[0]
                df[col].fillna(mode_val, inplace=True)
            except Exception:
                df[col].fillna(df[col].min(), inplace=True)
        else:
            # object / category
            try:
                mode_val = df[col].mode(dropna=True)[0]
                df[col].fillna(mode_val, inplace=True)
            except Exception:
                df[col].fillna("N/A", inplace=True)
    return df

if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            uploaded_file.seek(0)
            df = safe_read_csv(uploaded_file)
        else:
            # for excel
            df = pd.read_excel(uploaded_file, engine="openpyxl")

        st.subheader("Preview — original data")
        st.dataframe(df.head(), use_container_width=True)

        st.markdown("## Cleaning options")
        remove_dupes = st.checkbox("Remove duplicate rows", value=True)
        fix_encoding = st.checkbox("Try basic encoding fixes (strip weird whitespace)", value=True)
        infer_dates = st.checkbox("Try to infer/convert date columns", value=True)
        do_smart_fill = st.checkbox("Smart fill missing values (median/mode)", value=True)
        show_summary = st.checkbox("Show column summary (types, nulls, unique)", value=True)

        if remove_dupes:
            before = len(df)
            df = df.drop_duplicates()
            st.write(f"Removed {before - len(df)} duplicate rows")

        if fix_encoding:
            # simple whitespace/zero-width cleanup for strings
            def clean_str(x):
                if isinstance(x, str):
                    # remove zero-width and control characters
                    return x.replace("\u200b", "").strip()
                return x
            df = df.applymap(clean_str)

        if infer_dates:
            df = infer_and_convert_dates(df)

        if do_smart_fill:
            df = smart_fill(df)

        if show_summary:
            summary = pd.DataFrame({
                "dtype": df.dtypes.astype(str),
                "nulls": df.isnull().sum(),
                "unique": df.nunique(dropna=True)
            })
            st.subheader("Column summary")
            st.dataframe(summary)

        st.subheader("Preview — cleaned data")
        st.dataframe(df.head(), use_container_width=True)

        # download options: CSV or Excel
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download cleaned CSV", data=csv, file_name="cleaned_data.csv", mime="text/csv")

        try:
            import io
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="cleaned")
            buffer.seek(0)
            st.download_button("Download cleaned Excel (.xlsx)", data=buffer, file_name="cleaned_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception:
            # Excel export dependencies missing
            pass

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
