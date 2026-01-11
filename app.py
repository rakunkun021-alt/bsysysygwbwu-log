import streamlit as st
import requests, time, json, os

DB = "monitor_db.json"
def load():
    if os.path.exists(DB):
        try:
            with open(DB, "r") as f:
                d = json.load(f)
                if "groups" not in d: d["groups"] = {}
                if "h_id" not in d: d["h_id"] = []
                return d
        except: pass
    return {"groups": {}, "h_id": []}

def save(d):
    with open(DB, "w") as f: json.dump(d, f)

if 'db' not in st.session_state: st.session_state.db = load()
db = st.session_state.db

st.set_page_config(page_title="Monitor", layout="wide")
st.markdown('<style>.block-container{padding:0.5rem!important;} .stButton>button{width:100%!important; white-space:nowrap!important; min-height:35px!important;} .list-row{display:flex; align-items:center; background:#1e1e1e; border:1px solid #333; padding:5px 10px; border-radius:4px; margin-bottom:2px; flex-grow:1;} .dot{height:8px; width:8px; border-radius:50%; display:inline-block; margin-right:8px; flex-shrink:0;} .on{background:#0f0; box-shadow:0 0 4px #0f0;} .off{background:#f00;} .u-n{font-size:12px; color:#fff; font-weight:bold; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;} .btn-del>div>button{background:transparent!important; border:none!important; color:#f44!important; font-size:18px!important; min-height:unset!important; height:26px!important; width:26px!important;}</style>', unsafe_allow_html=True)

def notify(tk, ci, msg):
    if tk and ci:
        try: requests.post("https://api.telegram.org/bot"+tk+"/sendMessage", json={"chat_id":ci,"text":msg}, timeout=5)
        except: pass

with st.sidebar:
    st.header("Admin")
    with st.expander("➕ Grup"):
        gn = st.text_input("Nama")
        tk = st.text_input("Token")
        ci = st.text_input("ChatID")
        if st.button("Simpan Grup"):
            if gn and tk and ci:
                db["groups"][gn] = {"tk":tk, "ci":ci, "members":{}}
                save(db); st.rerun()
    if db["groups"]:
        target = st.selectbox
