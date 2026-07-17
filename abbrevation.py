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

.stApp{
    background: linear-gradient(
        135deg,
        #020617,
        #0f172a,
        #1e293b
    );
}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

/* Title */
.main-title{
    font-size:60px;
    font-weight:900;

    background:linear-gradient(
        90deg,
        #38bdf8,
        #67e8f9,
        #ffffff
    );

    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

/* Subtitle */
.sub-title{
    color:#cbd5e1;
    font-size:18px;
}

/* Card */
.card{
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:20px;
    padding:25px;
    margin-bottom:20px;
}

/* Upload */
.stFileUploader{
    background:rgba(255,255,255,0.04);
    padding:12px;
    border-radius:15px;
}

/* Metrics */
[data-testid="stMetric"]{
    background:rgba(255,255,255,0.05);
    border-radius:15px;
    padding:15px;
    border:1px solid rgba(255,255,255,0.08);
}

/* Download Button */
.stDownloadButton button{
    width:100%;
    background:linear-gradient(
        90deg,
        #06b6d4,
        #2563eb
    );

    color:white;
    border:none;
    border-radius:12px;
    height:50px;
    font-weight:bold;
    font-size:16px;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================

col1, col2 = st.columns([5, 1])

with col1:

    st.markdown("""
    <div class="main-title">
        Abbreviation Expansion Tool
    </div>

    <div class="sub-title">
        Smart Data Enrichment Utility for Standardizing Product and Business Attributes
    </div>
    """, unsafe_allow_html=True)

with col2:

    st.image(
        "https://pbs.twimg.com/media/GyJLJ06W4AAQRrN?format=png&name=large",
        width=180
    )

st.markdown("---")

# ==================================================
# HOW IT WORKS
# ==================================================

st.markdown("""
<div class="card">

<h3 style="color:white;">
📖 How It Works
</h3>

<p style="color:#cbd5e1;">
This tool automatically expands abbreviations into full forms using a mapping file provided by the user.
</p>

<h4 style="color:white;">
🚀 Steps to Use
</h4>

<ol style="color:#cbd5e1;">
<li>Upload the Input Excel file containing abbreviations or text.</li>
<li>Upload the Mapping Excel file.</li>
<li>The mapping file must contain <b>Short Form</b> and <b>Full Form</b> columns.</li>
<li>The application automatically scans and replaces abbreviations.</li>
<li>Review the output preview.</li>
<li>Download the processed Excel file.</li>
</ol>

<h4 style="color:white;">
📂 Example Mapping File
</h4>

<ul style="color:#cbd5e1;">
<li>AU → Australia</li>
<li>UK → United Kingdom</li>
<li>US → United States</li>
<li>UAE → United Arab Emirates</li>
</ul>

</div>
""", unsafe_allow_html=True)

# ==================================================
# FILE UPLOADS
# ==================================================

st.subheader("📂 Upload Files")

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

        with st.spinner("Processing files..."):

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

            output_df = input_df[input_column].apply(
                replace_abbreviations
            )

            output_df.columns = [
                "Original Text",
                "Updated Text"
            ]

        # ==========================================
        # SUCCESS
        # ==========================================

        st.success("✅ Processing completed successfully")

        # ==========================================
        # METRICS
        # ==========================================

        total_rows = len(output_df)

        updated_rows = (
            output_df["Original Text"] !=
            output_df["Updated Text"]
        ).sum()

        mapping_count = len(mapping_dict)

        m1, m2, m3 = st.columns(3)

        with m1:
            st.metric(
                "Rows Processed",
                total_rows
            )

        with m2:
            st.metric(
                "Rows Updated",
                updated_rows
            )

        with m3:
            st.metric(
                "Mapping Records",
                mapping_count
            )

        st.markdown("---")

        # ==========================================
        # PREVIEW
        # ==========================================

        st.subheader("📊 Output Preview")

        st.dataframe(
            output_df,
            use_container_width=True,
            height=500
        )

        # ==========================================
        # DOWNLOAD
        # ==========================================

        buffer = BytesIO()

        with pd.ExcelWriter(
            buffer,
            engine="openpyxl"
        ) as writer:

            output_df.to_excel(
                writer,
                index=False,
                sheet_name="Output"
            )

        buffer.seek(0)

        st.download_button(
            label="📥 Download Output File",
            data=buffer,
            file_name="Output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:

        st.error(f"❌ Error: {e}")

# ==================================================
# FOOTER
# ==================================================

st.markdown("""
<br><hr>

<p style="
text-align:center;
color:#94a3b8;
font-size:14px;
">
Pentland Data Enrichment Utility | Abbreviation Expansion Tool
</p>
""", unsafe_allow_html=True)
