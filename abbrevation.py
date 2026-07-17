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
    background: linear-gradient(
        135deg,
        #020617 0%,
        #0f172a 50%,
        #1e293b 100%
    );
}

/* Hide Streamlit branding */
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

/* Main Title */
.main-title{
    text-align:center;
    font-size:65px;
    font-weight:900;

    background:linear-gradient(
        90deg,
        #38bdf8,
        #67e8f9,
        #ffffff
    );

    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;

    margin-bottom:10px;
}

/* Subtitle */
.sub-title{
    text-align:center;
    color:#cbd5e1;
    font-size:20px;
    margin-bottom:35px;
}

/* Card */
.glass-card{
    background:rgba(255,255,255,0.05);
    backdrop-filter:blur(15px);
    border-radius:20px;
    padding:25px;
    border:1px solid rgba(255,255,255,0.1);
    margin-bottom:20px;
}

/* Download button */
.stDownloadButton button{
    width:100%;
    background:linear-gradient(
        90deg,
        #06b6d4,
        #2563eb
    );

    color:white;
    border:none;
    border-radius:10px;
    height:50px;
    font-size:16px;
    font-weight:bold;
}

/* Upload Box */
.stFileUploader{
    background:rgba(255,255,255,0.04);
    padding:10px;
    border-radius:15px;
}

/* Metrics */
[data-testid="stMetric"]{
    background:rgba(255,255,255,0.05);
    padding:15px;
    border-radius:15px;
    border:1px solid rgba(255,255,255,0.08);
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================

st.markdown("""
<div class="main-title">
    Abbreviation Expansion Tool
</div>

<div class="sub-title">
    Convert Short Forms into Standardized Full Forms Automatically
</div>
""", unsafe_allow_html=True)

# ==================================================
# UPLOAD CARD
# ==================================================

st.markdown("""
<div class="glass-card">
    <h3 style="color:white;">
        📂 Upload Files
    </h3>

    <p style="color:#cbd5e1;">
        Upload the source file and mapping file.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    input_file = st.file_uploader(
        "📄 Input File",
        type=["xlsx"]
    )

with col2:
    mapping_file = st.file_uploader(
        "📑 Mapping File",
        type=["xlsx"]
    )

# ==================================================
# PROCESS FILES
# ==================================================

if input_file and mapping_file:

    try:

        with st.spinner("Processing files..."):

            input_df = pd.read_excel(input_file)
            mapping_df = pd.read_excel(mapping_file)

            # ----------------------------------------
            # Clean Column Names
            # ----------------------------------------

            input_df.columns = input_df.columns.str.strip()
            mapping_df.columns = mapping_df.columns.str.strip()

            input_column = input_df.columns[0]

            # ----------------------------------------
            # Clean Mapping File
            # ----------------------------------------

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

            # ----------------------------------------
            # Create Dictionary
            # ----------------------------------------

            mapping_dict = dict(
                zip(
                    mapping_df["Short Form"],
                    mapping_df["Full Form"]
                )
            )

            # ----------------------------------------
            # Replace Abbreviations
            # ----------------------------------------

            def replace_abbreviations(text):

                original_text = str(text)
                updated_text = original_text

                for short_form, full_form in mapping_dict.items():

                    pattern = r"\\b" + re.escape(short_form) + r"\\b"

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

            # ----------------------------------------
            # Create Output
            # ----------------------------------------

            output_df = input_df[input_column].apply(
                replace_abbreviations
            )

            output_df.columns = [
                "Original Text",
                "Updated Text"
            ]

        # ==================================================
        # SUCCESS MESSAGE
        # ==================================================

        st.success(
            f"✅ Successfully processed {len(output_df)} records"
        )

        # ==================================================
        # METRICS
        # ==================================================

        rows_updated = (
            output_df["Original Text"]
            != output_df["Updated Text"]
        ).sum()

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Rows Processed",
                len(output_df)
            )

        with c2:
            st.metric(
                "Rows Updated",
                rows_updated
            )

        with c3:
            st.metric(
                "Mapping Entries",
                len(mapping_dict)
            )

        st.markdown("---")

        # ==================================================
        # RESULTS
        # ==================================================

        st.subheader("📊 Results Preview")

        st.dataframe(
            output_df,
            use_container_width=True,
            height=500
        )

        # ==================================================
        # CREATE DOWNLOAD FILE
        # ==================================================

        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:

            output_df.to_excel(
                writer,
                sheet_name="Output",
                index=False
            )

        output.seek(0)

        st.download_button(
            label="📥 Download Output File",
            data=output,
            file_name="Output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:

        st.error(f"❌ Error: {str(e)}")

# ==================================================
# FOOTER
# ==================================================

st.markdown("""
<br><br>
<hr>

<p style="
text-align:center;
color:#94a3b8;
font-size:14px;
">
Abbreviation Expansion Tool | Data Enrichment Automation
</p>
""", unsafe_allow_html=True)
