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
st.markdown('<style>.block-container{padding:1rem!important;} .stButton>button{width:100%!important; white-space:nowrap!important;} .dot{height:10px; width:10px; border-radius:50%; display:inline-block; margin-right:10px;} .on{background:#0f0;} .off{background:#f00;} .list-box{background:#262730; padding:10px; border-radius:5px; border-left:4px solid #444; margin-bottom:5px;}</style>', unsafe_allow_html=True)

def notify(tk, ci, msg):
    if tk and ci:
        try: requests.post("https://api.telegram.org/bot"+tk+"/sendMessage", json={"chat_id":ci,"text":msg}, timeout=5)
        except: pass

with st.sidebar:
    st.header("Admin")
    with st.expander("Grup"):
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
        if st.button("TAMBAH ID"):
            if uid.isdigit():
                try:
                    h = {"User-Agent": "Mozilla/5.0"}
                    r = requests.get("https://users.roblox.com/v1/users/"+uid, headers=h, timeout=10)
                    if r.status_code == 200:
                        db["groups"][target]["members"][uid] = {"name": r.json().get("name", uid), "last":-1}
                        if uid not in db["h_id"]: db["h_id"].append(uid)
                        save(db); st.rerun()
                except: pass

st.header("Roblox Monitor")
if not db["groups"]: st.info("Buka Sidebar untuk tambah grup.")

for gn, info in db["groups"].items():
    with st.expander(gn, expanded=True):
        m_list = info.get("members", {})
        if not m_list: continue
        uids = list(m_list.keys())
        try:
            res = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds":[int(x) for x in uids]}, timeout=10).json()
            pres = {str(p['userId']): p['userPresenceType'] for p in res.get('userPresences', [])}
            for u_id in uids:
                m = m_list[u_id]; cur = pres.get(u_id, 0)
                if m.get("last") == 2 and cur != 2 and m.get("last") != -1:
                    notify(info["
