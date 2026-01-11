import streamlit as st
import requests
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Roblox Grid Monitor", layout="wide")

# CSS KHUSUS AGAR TAMPILAN KOTAK KECIL 4 KE SAMPING DI HP
st.markdown("""
    <style>
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 4px !important;
    }
    [data-testid="column"] {
        flex: 1 1 23% !important;
        min-width: 75px !important;
        max-width: 24% !important;
        padding: 0px !important;
    }
    .stContainer {
        border: 1px solid #333;
        border-radius: 5px;
        padding: 5px;
        text-align: center;
        background-color: #0e1117;
    }
    </style>
    """, unsafe_allow_html=True)

def send_telegram(token, chat_id, message):
    if not token or not chat_id: return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=5)
    except: pass

# --- DATABASE ---
@st.cache_resource
def get_db():
    return {
        "groups": {"Utama": {"token": "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k", "chat_id": "8170247984", "members": {}}},
        "h_id": [], 
        "h_tk": ["8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k"], 
        "h_ci": ["8170247984"]
    }

db = get_db()

# --- SIDEBAR: KONFIGURASI ---
with st.sidebar:
    st.header("⚙️ Menu Admin")
    
    # 1. RIWAYAT TOKEN & CHAT ID (Menyatu dalam input)
    with st.expander("➕ Grup & Bot"):
        gn = st.text_input("Nama Grup:")
        
        # Selectbox Riwayat Bot
        tk = st.selectbox("Riwayat Token (Klik ^):", options=list(dict.fromkeys(db["h_tk"])))
        tk_new = st.text_input("Atau ketik Token baru:")
        
        ci = st.selectbox("Riwayat Chat ID (Klik ^):", options=list(dict.fromkeys(db["h_ci"])))
        ci_new = st.text_input("Atau ketik Chat ID baru:")
        
        f_tk = tk_new if tk_new else tk
        f_ci = ci_new if ci_new else ci

        if st.button("Simpan Grup"):
            if gn:
                db["groups"][gn] = {"token": f_tk, "chat_id": f_ci, "members": {}}
                if f_tk and f_tk not in db["h_tk"]: db["h_tk
