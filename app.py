import streamlit as st
import requests, time, json, os

DB = "monitor_db.json"
def load():
    if os.path.exists(DB):
        try:
            with open(DB, "r") as f: return json.load(f)
        except: return {"groups":{}, "h_tk":[], "h_id":[]}
    return {"groups":{}, "h_tk":[], "h_id":[]}

def save(d):
    with open(DB, "w") as f: json.dump(d, f)

if 'db' not in st.session_state: st.session_state.db = load()
db = st.session_state.db

st.set_page_config(page_title="Monitor", layout="wide")
st.markdown("""
<style>
    .block-container { padding: 0.5rem !important; }
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 2px !important; }
    [data-testid="column"] { flex: 1 1 25% !important; min-width: 0 !important; }
    .list-item { display: flex; align-items: center; border: 1px solid #333; background: #1e1e1e; padding: 2px 5px; border-radius: 2px; height: 26px; overflow: hidden; }
    .dot { height: 7px; width: 7px; border-radius: 50%; display: inline-block; margin-right: 5px; flex-shrink: 0; }
    .on { background: #0f0; box-shadow: 0 0 4px #0f0; }
    .off { background: #f00; }
    .u-n { font-size: 9px; font-weight: bold; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .stButton>button { background: transparent !important; border: none !important; color: #f44 !important; padding: 0 !important; font-size: 14px !important; height: 26px !important; width: 100% !important; }
</style>
""", unsafe_allow_html=True)

def notify(tk, ci, msg):
    if tk and ci:
        try: requests.post("https://api.telegram.org/bot"+tk+"/sendMessage", json={"chat_id":ci,"text":msg}, timeout=5)
        except: pass

with st.sidebar:
    st.header("Admin")
    with st.expander("Grup"):
        gn, tk, ci = st.text_input("Nama"), st.text_input("Token"), st.text_input("ChatID")
        if st.button("Simpan"):
            if gn and tk:
                db["groups"][gn] = {"tk":tk, "ci":ci, "members":{}}
                save(db); st
