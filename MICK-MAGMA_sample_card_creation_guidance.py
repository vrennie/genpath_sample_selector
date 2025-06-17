import streamlit as st
import pandas as pd
import streamlit_schedule
from entry_logger import log_entry, weekly_email_job

st.set_page_config(page_title="Clinic Code Checker", layout="wide")

# Auto weekly email dispatch
scheduler = streamlit_schedule.Schedule(key="weekly_email", interval="7d")
if scheduler.run():
    weekly_email_job()

# App styling
st.markdown("""
    <style>
    html, body, [class*="css"] { font-size: 22px !important; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .stTextInput > div > div > input {
        font-size: 24px !important; height: 50px !important; line-height: 50px !important; padding: 6px 14px !important;
    }
    label { font-size: 22px !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; font-size: 48px;'>🧬 PARR-TB Clinic Code Checker</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 20px;'>Checks clinic eligibility from the masterlist and tells you whether to create a sample card.</p>", unsafe_allow_html=True)

try:
    df = pd.read_excel("current_master_list.xlsx")
    df.columns = df.columns.str.strip().str.lower()

    if not {'clinic code', 'approved'}.issubset(set(df.columns)):
        st.error("❌ 'current_master_list.xlsx' must contain columns: 'Clinic Code' and 'Approved'")
    else:
        clinic_input = st.text_input("🏥 Enter Clinic Code (e.g., ABC123):").strip()

        if clinic_input:
            df['clinic code'] = df['clinic code'].astype(str).str.strip().str.upper()
            clinic_input_norm = clinic_input.upper()

            match = df[df['clinic code'] == clinic_input_norm]
            st.markdown("<div style='margin-top: 20px'></div>", unsafe_allow_html=True)

            if match.empty:
                st.markdown(
                    f"<div style='color: red; font-size: 28px; text-align: center;'>🚫 <b>{clinic_input}</b> is not in the PARR-TB study districts.<br><b>DO NOT create a sample card.</b></div>",
                    unsafe_allow_html=True
                )
                log_entry(clinic_input, is_in_district=False, is_approved=False)
            else:
                approved = str(match.iloc[0]['approved']).strip().lower()
                is_approved = approved in ['yes', 'approved', 'true', '1']
                if is_approved:
                    st.markdown(
                        f"<div style='color: green; font-size: 32px; text-align: center;'>✅ <b>{clinic_input}</b> is approved!<br><b>CREATE PATIENT CARD</b></div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<div style='color: orange; font-size: 28px; text-align: center;'>⚠️ <b>{clinic_input}</b> is in the list but has not approved.<br><b>Create a sample card.</b></div>",
                        unsafe_allow_html=True
                    )
                log_entry(clinic_input, is_in_district=True, is_approved=is_approved)

except FileNotFoundError:
    st.error("❌ Could not find 'current_master_list.xlsx'. Please ensure the file is in the app directory.")

