import streamlit as st
import requests, time, json, os

# --- DATABASE PERMANEN ---
DB = "monitor_db.json"

def load_data():
    if os.path.exists(DB):
        try:
            with open(DB, "r") as f:
                d = json.load(f)
                if "groups" not in d: d["groups"] = {}
                if "h_id" not in d: d["h_id"] = []
                return d
        except: pass
    return {"groups": {}, "h_id": []}

def save_data(d):
    with open(DB, "w") as f:
        json.dump(d, f)

# Inisialisasi
if 'db' not in st.session_state:
    st.session_state.db = load_data()
db = st.session_state.db

st.set_page_config(page_title="Roblox Monitor", layout="wide")

# CSS Minimalis (Hanya untuk titik status dan lebar kolom)
st.markdown("""
<style>
    .block-container { padding: 1rem !important; }
    .dot { height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-right: 5px; }
    .on { background-color: #00ff00; box-shadow: 0 0 5px #00ff00; }
    .off { background-color: #ff0000; }
    div[data-testid="column"] { width: auto !important; flex: unset !important; }
    .stExpander { border: 1px solid #333 !important; }
</style>
""", unsafe_allow_html=True)

def notify(tk, ci, msg):
    if tk and ci:
        try: requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", json={"chat_id":ci,"text":msg}, timeout=5)
        except: pass

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Admin")
    
    # 1. Management Grup
    with st.expander("➕ Tambah Grup Baru"):
        g_name = st.text_input("Nama Grup")
        g_token = st.text_input("Token Bot")
        g_chatid = st.text_input("Chat
