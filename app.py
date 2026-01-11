import streamlit as st
import requests, time, json, os

DB = "monitor_db.json"
def load():
    if os.path.exists(DB):
        try:
            with open(DB, "r") as f:
                d = json.load(f); return d
        except: pass
    return {"groups": {}, "h_id": []}

def save(d):
    with open(DB, "w") as f: json.dump(d, f)

if 'db' not in st.session_state: st.session_state.db = load()
db = st.session_state.db

st.set_page_config(page_title="Monitor", layout="wide")
st.markdown('<style>.block-container{padding:0.5rem!important;} .stButton>button{width:100%!important; white-space:nowrap!important;} .dot{height:10px; width:10px; border-radius:50%; display:inline-block; margin-right:8px;} .on{background:#0f0;} .off{background:#f00;} .list-row{display:flex; align-items:center; background:#1e1e1e; border:1px solid #333; padding:8px; border-radius:5px; margin-bottom:2px; flex-grow:1;}</style>', unsafe_allow_html=True)

def notify(tk, ci, msg):
    if tk and ci:
        try: requests.post("https://api.telegram.org/bot"+tk+"/sendMessage", json={"chat_id":ci,"text":msg}, timeout=5)
        except: pass

with st.sidebar:
    st.header("Admin")
    with st.expander("Grup", expanded=True):
        gn, tk, ci = st.text_input("Nama"), st.text_input("Token"), st.text_input("ChatID")
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
    with st.expander("Riwayat"):
        for hid in db["h_id"]:
            c1, c2 = st.columns([3,1]); c1.caption(hid)
            if c2.button("❌", key="h"+hid):
                db["h_id"].remove(hid); save(db); st.rerun()

st.header("Monitor")
for gn, info in db["groups"].items():
    with st.expander(gn, expanded=True):
        m_list = info.get("members", {})
        if not m_list: continue
        uids = list(m_list.keys())
        try:
            res = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds":[int(x) for x in uids]}, timeout=10).json()
            pres = {
