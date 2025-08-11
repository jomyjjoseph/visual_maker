import streamlit as st
import pandas as pd
import numpy as np
import re

st.set_page_config(page_title="Power BI Data Cleaner", layout="wide")

st.title("🧹 Data Cleaner for Power BI")

uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Read file
    if uploaded_file.name.endswith(".csv"):
        try:
            df = pd.read_csv(uploaded_file, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(uploaded_file, encoding="latin1")
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("📊 Data Preview")
    st.dataframe(df.head(10))

    st.markdown("---")
    st.subheader("⚙️ Cleaning Options")

    # Fill blanks / NaN
    fill_option = st.selectbox(
        "Fill blanks / NaN with:",
        ["Do nothing", "Median", "Mean", "Mode", "Custom value"]
    )
    if fill_option == "Custom value":
        custom_value = st.text_input("Enter custom value to fill blanks")

    # Remove columns
    cols_to_remove = st.multiselect(
        "Select columns to remove:",
        options=df.columns
    )

    # Remove special characters
    cols_to_clean = st.multiselect(
        "Select columns to remove special characters from:",
        options=df.columns
    )

    # Change column data type
    cols_to_change_type = st.multiselect(
        "Select columns to change data type:",
        options=df.columns
    )
    new_type = None
    if cols_to_change_type:
        new_type = st.selectbox("Select new type:", ["int", "float", "string", "datetime"])

    # Apply cleaning
    if st.button("🚀 Apply Cleaning"):
        cleaned_df = df.copy()

        # Fill blanks
        if fill_option != "Do nothing":
            if fill_option == "Median":
                cleaned_df = cleaned_df.fillna(cleaned_df.median(numeric_only=True))
            elif fill_option == "Mean":
                cleaned_df = cleaned_df.fillna(cleaned_df.mean(numeric_only=True))
            elif fill_option == "Mode":
                for col in cleaned_df.columns:
                    cleaned_df[col].fillna(cleaned_df[col].mode()[0], inplace=True)
            elif fill_option == "Custom value":
                cleaned_df = cleaned_df.fillna(custom_value)

        # Remove columns
        if cols_to_remove:
            cleaned_df.drop(columns=cols_to_remove, inplace=True)

        # Remove special characters
        for col in cols_to_clean:
            cleaned_df[col] = cleaned_df[col].astype(str).apply(lambda x: re.sub(r"[^a-zA-Z0-9\s]", "", x))

        # Change data type
        if cols_to_change_type and new_type:
            for col in cols_to_change_type:
                try:
                    if new_type == "int":
                        cleaned_df[col] = cleaned_df[col].astype(int)
                    elif new_type == "float":
                        cleaned_df[col] = cleaned_df[col].astype(float)
                    elif new_type == "string":
                        cleaned_df[col] = cleaned_df[col].astype(str)
                    elif new_type == "datetime":
                        cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors="coerce")
                except Exception as e:
                    st.warning(f"Could not convert column {col}: {e}")

        st.success("✅ Data cleaned successfully!")

        st.subheader("🔍 Cleaned Data Preview")
        st.dataframe(cleaned_df.head(10))

        # Download button
        csv = cleaned_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Cleaned CSV",
            data=csv,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )

else:
    st.info("Please upload a file to begin.")
