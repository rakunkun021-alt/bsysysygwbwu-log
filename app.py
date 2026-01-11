import streamlit as st
import requests
import time
import json

# --- CONFIG ---
st.set_page_config(page_title="Monitor 16:10 Pro", layout="wide")

# CSS: PAKSA 4 KOLOM DI HP & RASIO 16:10
st.markdown("""
<style>
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 6px !important;
    }
    [data-testid="column"] {
        width: calc(25% - 6px) !important;
        flex: 0 0 calc(25% - 6px) !important;
        min-width: calc(25% - 6px) !important;
        margin-bottom: 5px !important;
    }
    .card-roblox {
        border: 1px solid #444;
        border-radius: 6px;
        background-color: #1a1c24;
        padding: 8px 4px;
        aspect-ratio: 16 / 10;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }
    .user-row { display: flex; align-items: center; justify-content: center; gap: 4px; }
    .status-dot { height: 8px; width: 8px; border-radius: 50%; }
    .online { background-color: #2ecc71; box-shadow: 0 0 5px #2ecc71; }
    .offline { background-color: #e74c3c; }
    .username-text { font-size: 10px; font-weight: bold; color: white; overflow: hidden; }
    .id-text { font-size: 8px; color: #888; }
    .stButton > button { width: 100% !important; height: 22px !important; font-size: 8px !important; padding: 0px !important; }
</style>
""", unsafe_allow_html=True)

def send_telegram(token, chat_id, message):
    if not token or not chat_id: return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=5)
    except: pass

# --- DATABASE (ANTI HILANG) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "groups": {"Utama": {"token": "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k", "chat_id": "8170247984", "members": {}}},
        "h_id": []
    }
db = st.session_state.db

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Admin")
    with st.expander("💾 Backup & Restore"):
        st.code(json.dumps(db))
        res_code = st.text_area("Restore:")
        if st.button("Restore Now"):
            try:
                st.session_state.db = json.loads(res_code)
                st.rerun()
            except: st.error("Gagal")
    
    target = st.selectbox("Grup:", list(db["groups"].keys()))
    u_in = st.text_input("ID Roblox:")
    if st.button("Tambah"):
        if u_in.isdigit():
            try:
                res = requests.get(f"
