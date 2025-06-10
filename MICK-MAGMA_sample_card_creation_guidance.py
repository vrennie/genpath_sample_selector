import streamlit as st
import pandas as pd

st.set_page_config(page_title="Clinic Code Checker", layout="wide")

# --- Ultra-scale with fixed input alignment ---
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-size: 36px !important;
    }
    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
    }
    .stTextInput > div > div > input {
        font-size: 36px !important;
        height: 80px !important;
        line-height: 80px !important;
        padding: 10px 20px !important;
    }
    label {
        font-size: 36px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- App title ---
st.markdown("<h1 style='text-align: center; font-size: 72px;'>🧬 PARR-TB Clinic Code Checker</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 32px;'>Upload the masterlist and enter a clinic code to get guidance on sample cards.</p>", unsafe_allow_html=True)

# --- File upload ---
uploaded_file = st.file_uploader("📁 Upload the PARR-TB clinic masterlist Excel file", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip().str.lower()

        required_cols = {'clinic code', 'approved'}
        if not required_cols.issubset(set(df.columns)):
            st.error("❌ Excel must contain columns: 'Clinic Code' and 'Approved'")
        else:
            clinic_input = st.text_input("🏥 Enter Clinic Code (e.g., ABC123):").strip()

            if clinic_input:
                df['clinic code'] = df['clinic code'].astype(str).str.strip().str.upper()
                clinic_input_norm = clinic_input.upper()

                match = df[df['clinic code'] == clinic_input_norm]
                st.markdown("<div style='margin-top: 40px'></div>", unsafe_allow_html=True)

                if match.empty:
                    st.markdown(
                        f"<div style='color: red; font-size: 48px; text-align: center;'>🚫 <b>{clinic_input}</b> is not in the PARR-TB study districts.<br><b>DO NOT create a sample card.</b></div>",
                        unsafe_allow_html=True
                    )
                else:
                    approved = str(match.iloc[0]['approved']).strip().lower()
                    if approved in ['yes', 'approved', 'true', '1']:
                        st.markdown(
                            f"<div style='color: green; font-size: 56px; text-align: center;'>✅ <b>{clinic_input}</b> is approved!<br><b>CREATE PATIENT CARD</b></div>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"<div style='color: orange; font-size: 48px; text-align: center;'>⚠️ <b>{clinic_input}</b> is in the list but has not approved.<br><b>DO NOT create a sample card.</b></div>",
                            unsafe_allow_html=True
                        )
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.info("📤 Please upload the PARR-TB clinic masterlist Excel file to begin.")
