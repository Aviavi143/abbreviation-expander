import streamlit as st
import pandas as pd
import re
from io import BytesIO

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Abbreviation Expander",
    page_icon="📘",
    layout="wide"
)

st.title("📘 Abbreviation Expansion Tool")

st.write(
    "Upload an input file and a mapping file to replace abbreviations with full forms."
)

# =====================================
# FILE UPLOADS
# =====================================

input_file = st.file_uploader(
    "Upload Input File",
    type=["xlsx"]
)

mapping_file = st.file_uploader(
    "Upload Mapping File",
    type=["xlsx"]
)

# =====================================
# PROCESS FILES
# =====================================

if input_file and mapping_file:

    try:

        input_df = pd.read_excel(input_file)
        mapping_df = pd.read_excel(mapping_file)

        # -----------------------------
        # Clean column names
        # -----------------------------

        input_df.columns = input_df.columns.str.strip()
        mapping_df.columns = mapping_df.columns.str.strip()

        input_column = input_df.columns[0]

        # -----------------------------
        # Clean mapping data
        # -----------------------------

        mapping_df["Short Form"] = (
            mapping_df["Short Form"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        mapping_df["Full Form"] = (
            mapping_df["Full Form"]
            .astype(str)
            .str.strip()
        )

        # -----------------------------
        # Create mapping dictionary
        # -----------------------------

        mapping_dict = dict(
            zip(
                mapping_df["Short Form"],
                mapping_df["Full Form"]
            )
        )

        # -----------------------------
        # Replacement Function
        # -----------------------------

        def replace_abbreviations(text):

            original_text = str(text)
            updated_text = original_text

            for short_form, full_form in mapping_dict.items():

                pattern = r"\b" + re.escape(short_form) + r"\b"

                updated_text = re.sub(
                    pattern,
                    full_form,
                    updated_text,
                    flags=re.IGNORECASE
                )

            return pd.Series([
                original_text,
                updated_text
            ])

        # -----------------------------
        # Generate output
        # -----------------------------

        output_df = input_df[input_column].apply(
            replace_abbreviations
        )

        output_df.columns = [
            "Original Text",
            "Updated Text"
        ]

        st.success("✅ Processing Complete")

        st.subheader("Preview")

        st.dataframe(
            output_df,
            use_container_width=True
        )

        # -----------------------------
        # Create downloadable Excel
        # -----------------------------

        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:

            output_df.to_excel(
                writer,
                index=False,
                sheet_name="Output"
            )

        output.seek(0)

        st.download_button(
            label="📥 Download Output",
            data=output,
            file_name="Output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:

        st.error(f"Error: {e}")
