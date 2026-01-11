import streamlit as st
import requests
import time
import json

# --- CONFIG & UI STYLE ---
st.set_page_config(page_title="Roblox Monitor 16:10", layout="wide")

# CSS UNTUK GRID KONSISTEN 4 KOLOM & RASIO 16:10
st.markdown("""
    <style>
    /* Paksa Grid agar selalu 4 kolom di baris manapun */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 5px !important;
        justify-content: flex-start !important;
    }
    /* Mengunci ukuran kolom 24% agar tidak membesar sendiri */
    [data-testid="column"] {
        flex: 0 0 24% !important;
        min-width: 80px !important;
        max-width: 24% !important;
        padding: 0px !important;
        margin-bottom: 10px !important;
    }
    /* Box Rasio 16:10 */
    .card-roblox {
        border: 1px solid #444;
        border-radius: 6px;
        background-color: #1a1c24;
        padding: 8px;
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
        font-size: 11px;
        font-weight: bold;
        color: white;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .id-text { font-size: 9px; color: #888; margin-top: 2px; }
    /* Style Tombol Hapus */
    .stButton > button {
        width: 100% !important;
        height: 22px !important;
        font-size: 10px !important;
        padding: 0px !important;
        margin-top: 2px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def send_telegram(token, chat_id, message):
    if not token or not chat_id:
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {"chat_id": chat_id, "text
