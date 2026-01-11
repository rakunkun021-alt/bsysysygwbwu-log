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
st.markdown('<style>.block-container{padding:0.5rem!important;} .stButton>button{width:100%!important; white-space:nowrap!important;} .dot{height:8px; width:8px; border-radius:50%; display:inline-block; margin-right:5px;} .on{background:#0f0;} .off{background:#f00;} .list-row{display:flex; align-items:center; background:#1e1e1e; border:1px solid #333; padding:5px; border-radius:4px; margin-bottom:2px;}</style>', unsafe_allow_html=True)

def notify(tk, ci, msg):
    if tk and ci:
        try: requests.post("https://api.telegram.org/bot"+tk+"/sendMessage", json={"chat_id":ci,"text":msg}, timeout=5)
        except: pass

with st.sidebar:
    st.header("Admin")
    with st.expander("Grup", expanded=True):
        gn = st.text_input("Nama")
        tk = st.text_input("Token")
        ci = st.text_input("ChatID")
        if st.button("SIMPAN"):
            if gn and tk and ci:
                db["groups"][gn] = {"tk":tk, "ci":ci, "members":{}}
                save(db); st.rerun()
    if db["groups"]:
        target = st.selectbox("Pilih", list(db["groups"].keys()))
        uid = st.text_input("ID Roblox")
        if st.button("TAMBAH"):
            if uid.isdigit():
                try:
                    r = requests.get("https://users.roblox.com/v1/users/"+uid, headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
                    if r.status_code == 200:
                        db["groups"][target]["members"][uid] = {"name": r.json().get("name", uid), "last":-1}
                        if uid not in db["h_id"]: db["h_id"].append(uid)
                        save(db); st.rerun()
                except: pass

st.header("Monitor")
if not db["groups"]: st.info("Isi data di Sidebar.")

for gn, info in db["groups"].items():
    with st.expander(gn, expanded=True):
        m_list = info.get("members", {})
        if not m_list: continue
        uids = list(m_list.keys())
        try:
