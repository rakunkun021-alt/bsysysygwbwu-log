import streamlit as st
import requests
import time
import json

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Roblox Monitor 16:10", layout="wide")

# CSS UNTUK GRID 4 KOLOM KONSISTEN & RASIO 16:10
st.markdown("""
    <style>
    /* Mengunci Grid agar tetap 4 kolom dan tidak melar jika cuma ada 1 ID */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
        justify-content: flex-start !important;
    }
    [data-testid="column"] {
        flex: 0 0 calc(25% - 10px) !important;
        min-width: 80px !important;
        max-width: calc(25% - 10px) !important;
        padding: 0px !important;
        margin-bottom: 10px !important;
    }
    
    /* Box dengan Rasio 16:10 */
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
    
    /* Indikator Samping Nama */
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
    
    /* Tombol Hapus */
    .stButton > button {
        width: 100% !important;
        height: 24px !important;
        font-size: 11px !important;
        padding: 0px !important;
        margin-top: 5px !important;
        border: none !important;
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
        requests.post(url, json=payload,
