import streamlit as st
import requests, time, json, os

DB = "monitor_db.json"
def load():
    if os.path.exists(DB):
        try:
            with open(DB, "r") as f: return json.load(f)
        except: return {"groups": {}, "h_tk": [], "h_id": []}
    return {"groups": {}, "h_tk": [], "h_id": []}

def save(d):
    with open(DB, "w") as f: json.dump(d, f)

if 'db' not in st.session_state: st.session_state.db = load()
db = st.session_state.db

st.set_page_config(page_title="Monitor", layout="wide")
st.markdown("""
<style>
    .block-container { padding: 0.5rem !important; }
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 3px !important; }
    [data-testid="column"] { width: 25% !important; flex: 1 1 25% !important; min-width: 0px !important; }
    .card { border: 1px solid #444; border-radius: 4px; background: #1a1c24; aspect-ratio: 16/10; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 2px; }
    .dot { height: 5px; width: 5px; border-radius: 50%; display: inline-block; margin-right: 2px; }
    .on { background: #2ecc71; box-shadow: 0 0 3px #2ecc71; }
    .off { background: #e74c3c; }
    .u-n { font-size: 7px; font-weight: bold; color: white; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 95%; text-align: center; }
    .u-i { font-size: 5px; color: #888; text-align: center; }
    .stButton>button { width: 100% !important; background: transparent !important; border: 0.5px solid #444 !important; color: #ff4b4b !important; height: 16px !important; font-size: 8px !important; padding: 0 !important; margin-top: 2px !important; }
</style>
""", unsafe_allow_html=True)

def notify(tk, ci, msg):
    if tk and ci:
        try: requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", json={"chat_id":ci, "text":msg}, timeout=5)
        except: pass

with st.sidebar:
    st.header("⚙️ Admin")
    with st.expander("➕ Tambah Grup"):
        gn, tk, ci = st.text_input("Grup"), st.text_input("Token"), st.text_input("ChatID")
        if st.button("Simpan"):
            if gn and tk:
                db["groups"][gn] = {"tk": tk, "ci": ci, "members": {}}
                if tk not in db["h_tk"]: db["h_tk"].append(tk)
                save(db); st.rerun()
    if db["groups"]:
        target = st.selectbox("Pilih Grup", list(db["groups"].keys()))
        uid = st.text_input("ID")
        if st.button("Tambah ID"):
            if uid.isdigit():
                try:
                    res = requests.get(f"
