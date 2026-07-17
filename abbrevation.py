import streamlit as st
import pandas as pd
import re
from io import BytesIO

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Abbreviation Expansion Tool",
    page_icon="📘",
    layout="wide"
)

# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

/* Background */
.stApp{
    background: #0f172a;
}

/* Hide Streamlit elements */
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

/* Header */
.main-title{
    font-size:52px;
    font-weight:800;
    color:white;
    margin-bottom:5px;
}

.sub-title{
    color:#94a3b8;
    font-size:16px;
}

/* Uploaders */
.stFileUploader{
    background:#111827;
    border-radius:12px;
    padding:15px;
}

/* Metrics */
[data-testid="stMetric"]{
    background:#111827;
    border:1px solid #1f2937;
    border-radius:12px;
    padding:12px;
}

/* Dataframe */
[data-testid="stDataFrame"]{
    border:1px solid #1f2937;
    border-radius:12px;
}

/* Download Button */
.stDownloadButton button{
    width:100%;
    height:50px;
    background:#2563eb;
    color:white;
    border:none;
    border-radius:10px;
    font-weight:bold;
}

hr{
    border-color:#1f2937;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================

col1, col2 = st.columns([6,1])

with col1:
    st.markdown("""
    <div class="main-title">
        Abbreviation Expansion Tool
    </div>

    <div class="sub-title">
        Expand short forms into standardized values
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.image(
        "https://pbs.twimg.com/media/GyJLJ06W4AAQRrN?format=png&name=large",
        width=130
    )

st.divider()

# ==================================================
# QUICK INSTRUCTIONS
# ==================================================

st.info("""
1️⃣ Upload Input File

2️⃣ Upload Mapping File

3️⃣ Download Processed Output
""")

# ==================================================
# FILE UPLOAD SECTION
# ==================================================

col1, col2 = st.columns(2)

with col1:
    input_file = st.file_uploader(
        "Input File (.xlsx)",
        type=["xlsx"]
    )

with col2:
    mapping_file = st.file_uploader(
        "Mapping File (.xlsx)",
        type=["xlsx"]
    )

# ==================================================
# PROCESS FILES
# ==================================================

if input_file and mapping_file:

    try:

        with st.spinner("Processing..."):

            input_df = pd.read_excel(input_file)
            mapping_df = pd.read_excel(mapping_file)

            input_df.columns = input_df.columns.str.strip()
            mapping_df.columns = mapping_df.columns.str.strip()

            input_column = input_df.columns[0]

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

            mapping_dict = dict(
                zip(
                    mapping_df["Short Form"],
                    mapping_df["Full Form"]
                )
            )

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

            output_df = input_df[input_column].apply(
                replace_abbreviations
            )

            output_df.columns = [
                "Original Text",
                "Updated Text"
            ]

        # ==========================================
        # METRICS
        # ==========================================

        total_rows = len(output_df)

        updated_rows = (
            output_df["Original Text"]
            != output_df["Updated Text"]
        ).sum()

        mapping_count = len(mapping_dict)

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Rows Processed",
                total_rows
            )

        with c2:
            st.metric(
                "Rows Updated",
                updated_rows
            )

        with c3:
            st.metric(
                "Mappings",
                mapping_count
            )

        st.divider()

        # ==========================================
        # RESULTS
        # ==========================================

        st.subheader("Results")

        st.dataframe(
            output_df,
            use_container_width=True,
            height=450
        )

        # ==========================================
        # DOWNLOAD FILE
        # ==========================================

        excel_buffer = BytesIO()

        with pd.ExcelWriter(
            excel_buffer,
            engine="openpyxl"
        ) as writer:

            output_df.to_excel(
                writer,
                index=False,
                sheet_name="Output"
            )

        excel_buffer.seek(0)

        st.download_button(
            label="📥 Download Output",
            data=excel_buffer,
            file_name="Output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:

        st.error(f"Error: {str(e)}")

# ==================================================
# FOOTER
# ==================================================

st.markdown(
    """
    <br>
    <hr>
    <center style='color:#94a3b8;'>
    Pentland Data Enrichment Utility
    </center>
    """,
    unsafe_allow_html=True
)
