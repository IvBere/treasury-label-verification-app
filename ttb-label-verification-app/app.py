import json
from datetime import datetime

import pandas as pd
import streamlit as st

from verifier import STANDARD_WARNING, verify_label

st.set_page_config(page_title="TTB Label Verification", page_icon="🏛️", layout="wide")

st.title("TTB Alcohol Label Verification Prototype")
st.caption("AI-assisted field matching for alcohol beverage label review. No files are stored by this prototype.")

with st.sidebar:
    st.header("How to use")
    st.write("1. Paste label text or upload a .txt file.")
    st.write("2. Enter expected application fields.")
    st.write("3. Run verification and review pass/review/fail results.")
    st.divider()
    st.write("Prototype scope: text-based verification with fuzzy matching and rules for required warning language.")

uploaded_file = st.file_uploader("Upload label text file (.txt)", type=["txt"])
label_text = ""
if uploaded_file is not None:
    label_text = uploaded_file.read().decode("utf-8", errors="ignore")

sample = """OLD TOM DISTILLERY
Kentucky Straight Bourbon Whiskey
45% Alc./Vol. (90 Proof)
750 mL
Bottled by Old Tom Distillery, Louisville, KY
GOVERNMENT WARNING: (1) ACCORDING TO THE SURGEON GENERAL, WOMEN SHOULD NOT DRINK ALCOHOLIC BEVERAGES DURING PREGNANCY BECAUSE OF THE RISK OF BIRTH DEFECTS. (2) CONSUMPTION OF ALCOHOLIC BEVERAGES IMPAIRS YOUR ABILITY TO DRIVE A CAR OR OPERATE MACHINERY, AND MAY CAUSE HEALTH PROBLEMS.
"""

if st.button("Load sample label"):
    label_text = sample

label_text = st.text_area("Label text", value=label_text, height=260, placeholder="Paste OCR text or label copy here...")

st.subheader("Application Data to Verify")
col1, col2 = st.columns(2)
with col1:
    brand_name = st.text_input("Brand name", value="OLD TOM DISTILLERY")
    class_type = st.text_input("Class/type", value="Kentucky Straight Bourbon Whiskey")
    alcohol_content = st.text_input("Alcohol content", value="45% Alc./Vol. (90 Proof)")
with col2:
    net_contents = st.text_input("Net contents", value="750 mL")
    producer_address = st.text_input("Producer/bottler name and address", value="Old Tom Distillery, Louisville, KY")
    country_of_origin = st.text_input("Country of origin, if imported", value="")

application_data = {
    "brand_name": brand_name,
    "class_type": class_type,
    "alcohol_content": alcohol_content,
    "net_contents": net_contents,
    "producer_address": producer_address,
    "country_of_origin": country_of_origin,
}

if st.button("Run Verification", type="primary"):
    if not label_text.strip():
        st.error("Please paste label text or upload a .txt file before running verification.")
    else:
        report = verify_label(label_text, application_data)
        status = report["overall_status"]
        if status == "Pass":
            st.success("Overall status: Pass")
        elif status == "Review":
            st.warning("Overall status: Review")
        else:
            st.error("Overall status: Fail")

        st.subheader("Verification Results")
        df = pd.DataFrame(report["results"])
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.subheader("Detected Patterns")
        st.json(report["detected_patterns"])

        st.subheader("Required Government Warning Reference")
        st.code(STANDARD_WARNING)

        export = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "application_data": application_data,
            "verification_report": report,
        }
        st.download_button(
            "Download verification report JSON",
            data=json.dumps(export, indent=2),
            file_name="ttb_label_verification_report.json",
            mime="application/json",
        )
