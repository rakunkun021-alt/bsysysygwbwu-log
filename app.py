import streamlit as st
import requests
import time
import json

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Roblox Monitor 16:10", layout="wide")

# CSS UNTUK GRID 4 KOLOM KONSISTEN & RASIO 16:10
st.markdown("""
    <style>
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
        justify-content: flex-start !important;
    }
    /* Mengunci kolom agar tetap 1/4 lebar layar (24%) agar tidak melar */
    [data-testid="column"] {
        flex: 0 0 24% !important;
        min-width: 80px !important;
        max-width: 24% !important;
        padding: 0px !important;
        margin-bottom: 10px !important;
    }
    .card-roblox {
        border: 1px solid #444;
        border-radius: 8px;
        background-color: #1a1c24;
        padding: 10px;
        aspect-ratio: 16 / 10;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }
    .user-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        width: 100%;
    }
    .status-dot {
        height: 10px;
        width: 10px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .online { background-color: #2ecc71; box-shadow: 0 0 5px #2ecc71; }
    .offline { background-color: #e74c3c; }
    .username-text {
        font-size: 12px;
        font-weight: bold;
        color: white;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .id-text { font-size: 10px; color: #888; margin-top: 2px; }
    .stButton > button {
        width: 100% !important;
        height: 24px !important;
        font-size: 11px !important;
        padding: 0px !important;
        margin-top: 5px !important;
        background-color: #2d3139 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def send_telegram(token, chat_id, message):
    if not token or not chat_id:
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        requests.post(url, json=payload, timeout=5)
    except:
        pass

# --- DATABASE SESSION ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "groups": {"Utama": {"token": "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k", "chat_id": "8170247984", "members": {}}},
        "h_id": [], 
        "h_tk": ["8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k"], 
        "h_ci": ["8170247984"]
    }

db = st.session_state.db

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Admin Panel")
    
    with st.expander("💾 Backup & Restore (Anti Hilang)"):
        st.caption("Salin kode ini ke Catatan HP:")
        st.code(json.dumps(db))
        res_code = st.text_input("Tempel kode restore:")
        if st.button("Restore Data"):
            if res_code:
                try:
                    st.session_state.db = json.loads(res_code)
                    st.rerun()
                except:
                    st.error("Format salah")

    with st.expander("🤖 Set Bot & Grup"):
        gn = st.text_input("Nama Grup Baru:")
        tk_s = st.selectbox("Riwayat Token:", options=db["h_tk"])
        tk_n = st.text_input("Atau Token Baru:")
        ci_s = st.selectbox("Riwayat Chat ID:", options=db["h_ci"])
        ci_n = st.text_input("Atau Chat ID Baru:")
        
        if st.button("Simpan Konfigurasi"):
            if gn:
                ft = tk_n
