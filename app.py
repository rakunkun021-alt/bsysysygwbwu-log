import streamlit as st
import requests
import time
import json

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Roblox Monitor 16:10", layout="wide")

# CSS UNTUK MENGUNCI 4 KOLOM & RASIO 16:10
st.markdown("""
    <style>
    /* Mengatur container agar bisa membungkus kolom secara rapi */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 12px !important;
        justify-content: flex-start !important;
    }
    
    /* Mengunci lebar kolom agar selalu 4 kolom per baris */
    [data-testid="column"] {
        flex: 0 0 calc(25% - 15px) !important;
        min-width: 150px !important;
        max-width: calc(25% - 15px) !important;
        margin-bottom: 10px !important;
    }

    /* Box Monitoring Rasio 16:10 */
    .card-roblox {
        border: 1px solid #444;
        border-radius: 10px;
        background-color: #1a1c24;
        padding: 15px;
        aspect-ratio: 16 / 10;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        width: 100%;
    }
    
    .user-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        margin-bottom: 5px;
    }
    .status-dot { height: 12px; width: 12px; border-radius: 50%; }
    .online { background-color: #2ecc71; box-shadow: 0 0 8px #2ecc71; }
    .offline { background-color: #e74c3c; }
    
    .username-text { font-size: 14px; font-weight: bold; color: white; }
    .id-text { font-size: 11px; color: #888; }
    
    /* Tombol Hapus rapi */
    .stButton > button {
        width: 100% !important;
        height: 28px !important;
        font-size: 11px !important;
        margin-top: 5px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def send_telegram(token,
