import streamlit as st
import requests, time, json, os

# --- PERSISTENT DATABASE ---
DB = "monitor_db.json"
def load_db():
    if os.path.exists(DB):
        with open(DB, "r") as f: return json.load(f)
    return {"groups": {}, "h_tk": [], "h_id": []}

def save_db(data):
    with open(DB, "w") as f: json.dump(data, f)

if 'db' not in st.session_state:
    st.session_state.db = load_db()
db = st.session_state.db

# --- UI CONFIG (4 KOLOM & 16:10) ---
st.set_page_config(page_title="Roblox Monitor", layout="wide")
st.markdown("""
<style>
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: wrap !important; gap: 8px !important; }
    [data-testid="column"] { width: calc(25% - 10px) !important; flex: 0 0 calc(25% - 10px) !important; min-width: calc(25% - 10px) !important; margin-bottom: 10px !important; }
    .card { border: 1px solid #444; border-radius: 8px; background: #1a1c24; aspect-ratio: 16 / 10; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 5px; }
    .dot { height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-right: 5px; }
    .on { background: #2ecc71; box-shadow: 0 0 8px #2ecc71; }
    .off { background: #e74c3c; }
    .u-n { font-size: 12px; font-weight: bold; color: white; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 90%; }
    .u-i { font-size: 9px; color: #888; }
    .stButton>button { width: 100% !important; height: 22px !important; font-size: 9px !important; padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

def send_tg(tk, ci, msg):
    try: requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", json={"chat_id":ci, "text":msg}, timeout=5)
    except: pass

# --- SIDEBAR: MANAGEMENT ---
with st.sidebar:
    st.title("⚙️ Admin")
    with st.expander("➕ Tambah Grup"):
        gn = st
