import pandas as pd
import re

# =====================================
# READ FILES
# =====================================

input_df = pd.read_excel("Input.xlsx")
mapping_df = pd.read_excel("Mapping.xlsx")

# =====================================
# CLEAN COLUMN NAMES
# =====================================

input_df.columns = input_df.columns.str.strip()
mapping_df.columns = mapping_df.columns.str.strip()

# =====================================
# GET INPUT COLUMN
# =====================================

input_column = input_df.columns[0]

# =====================================
# CLEAN MAPPING DATA
# =====================================

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

# =====================================
# CREATE MAPPING DICTIONARY
# =====================================

mapping_dict = dict(
    zip(
        mapping_df["Short Form"],
        mapping_df["Full Form"]
    )
)

print("\nMapping Dictionary:")
print(mapping_dict)

# =====================================
# REPLACEMENT FUNCTION
# =====================================

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

# =====================================
# APPLY REPLACEMENT
# =====================================

output_df = input_df[input_column].apply(
    replace_abbreviations
)

# =====================================
# COLUMN NAMES
# =====================================

output_df.columns = [
    "Original Text",
    "Updated Text"
]

# =====================================
# SAVE OUTPUT
# =====================================

output_df.to_excel(
    "Output.xlsx",
    index=False
)

# =====================================
# DISPLAY OUTPUT
# =====================================

pd.set_option("display.max_columns", None)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.width", None)

print("\nOUTPUT PREVIEW\n")
print(output_df.to_string(index=False))

print("\n✅ Output.xlsx created successfully")