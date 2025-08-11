import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Smart Data Cleaner", page_icon="🧹")
st.title("🧹 Smart Data Cleaner for Power BI")

uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Load file
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, encoding="utf-8", errors="replace")
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("📄 Preview of Original Data")
        st.dataframe(df.head())

        # Cleaning
        st.markdown("### 🛠 Cleaning Options")
        if st.checkbox("Remove duplicate rows"):
            df = df.drop_duplicates()

        if st.checkbox("Fix encoding issues"):
            df = df.applymap(lambda x: str(x).encode("latin1", errors="ignore").decode("utf-8") if isinstance(x, str) else x)

        if st.checkbox("Smart fill missing values"):
            for col in df.columns:
                if df[col].isnull().sum() > 0:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        median_val = df[col].median()
                        df[col].fillna(median_val, inplace=True)
                    elif pd.api.types.is_datetime64_any_dtype(df[col]):
                        mode_val = df[col].mode()[0] if not df[col].mode().empty else pd.NaT
                        df[col].fillna(mode_val, inplace=True)
                    else:  # text or object type
                        mode_val = df[col].mode()[0] if not df[col].mode().empty else "N/A"
                        df[col].fillna(mode_val, inplace=True)

        st.subheader("✅ Cleaned Data Preview")
        st.dataframe(df.head())

        # Download cleaned file
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Cleaned CSV",
            data=csv,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
