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
st.markdown('<style>.block-container{padding:1rem!important;} .stButton>button{width:100%!important; white-space:nowrap!important;} .dot{height:10px; width:10px; border-radius:50%; display:inline-block; margin-right:10px;} .on{background:#0f0;} .off{background:#f00;} .list-row{background:#262730; padding:10px; border-radius:5px; border-left:4px solid #444; margin-bottom:5px; flex-grow:1; display:flex; align-items:center;}</style>', unsafe_allow_html=True)

def notify(tk, ci, msg):
    if tk and ci:
        try: requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", json={"chat_id":ci,"text":msg}, timeout=5)
        except: pass

with st.sidebar:
    st.header("Admin")
    with st.expander("Grup", expanded=True):
        gn = st.text_input("Nama")
        tk = st.text_input("Token")
        ci = st.text_input("ChatID")
        if st.button("SIMPAN GRUP"):
            if gn and tk and ci:
                db["groups"][gn] = {"tk":tk, "ci":ci, "members":{}}
                save(db); st.rerun()
    if db["groups"]:
        st.write("---")
        target = st.selectbox("Pilih", list(db["groups"].keys()))
        uid = st.text_input("ID Roblox")
        if st.button("
