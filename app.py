import streamlit as st
import requests
import time
import json

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Roblox Monitor Pro", layout="wide")

# CSS UNTUK GRID 4 KOLOM & INDIKATOR SAMPING NAMA
st.markdown("""
<style>
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 10px !important;
        justify-content: flex-start !important;
    }
    [data-testid="column"] {
        flex: 0 0 calc(25% - 15px) !important;
        min-width: 150px !important;
        max-width: calc(25% - 15px) !important;
        margin-bottom: 15px !important;
    }
    .card-roblox {
        border: 1px solid #444;
        border-radius: 8px;
        background-color: #1a1c24;
        padding: 12px;
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
        gap: 8px;
        width: 100%;
    }
    .status-dot {
        height: 12px;
        width: 12px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .online { background-color: #2ecc71; box-shadow: 0 0 8px #2ecc71; }
    .offline { background-color: #e74c3c; }
    .username-text {
        font-size: 13px;
        font-weight: bold;
        color: white;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .id-text { font-size: 10px; color: #888; margin-top: 4px; }
    .stButton > button {
        width: 100% !important;
        height: 26px !important;
        font-size: 11px !important;
        padding: 0px !important;
        margin-top: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

def send_telegram(token, chat_id, message):
    if not token or not chat_id: return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=5)
    except: pass

# --- DATABASE SESSION ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "groups": {"Utama": {"token": "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k", "chat_id": "8170247984", "members": {}}},
        "h_id": [], 
        "h_tk": ["8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k"], 
        "h_ci": ["8170247984"]
    }

db = st.session_state.db

# --- SIDEBAR (ADMIN PANEL) ---
with st.sidebar:
    st.header("⚙️ Admin Panel")
    
    # 1. Fitur Anti-Hilang (Sesuai ID Anda)
    with st.expander("💾 Backup & Restore (Anti Hilang)"):
        st.
