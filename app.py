import streamlit as st

st.set_page_config(page_title="Eval-IA", layout="wide")
# Hack CSS
st.markdown("""
    <style>
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    </style>
""", unsafe_allow_html=True)
st.title("📊 Eval-IA App")
st.markdown("Welcome buddy, use the panel on the left:")
st.markdown("- 📌 Création : définir vos projets et solutions")
st.markdown("- 📊 Visualisation : explorer les solutions et décider")

