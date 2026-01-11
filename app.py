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
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: wrap !important; gap: 4px !important; }
    [data-testid="column"] { width: calc(25% - 4px) !important; flex: 0 0 calc(25% - 4px) !important; min-width: 60px !important; margin-bottom: 4px !important; }
    .card { border: 1px solid #444; border-radius: 4px; background: #1a1c24; aspect-ratio: 16/10; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 2px; }
    .dot { height: 6px; width: 6px; border-radius: 50%; display: inline-block; margin-right: 2px; }
    .on { background: #2ecc71; box-shadow: 0 0 4px #2ecc71; }
    .off { background: #e74c3c; }
    .u-n { font-size: 8px; font-weight: bold; color: white; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 95%; }
    .u-i { font-size: 6px; color: #888; margin-top: 1px; }
    .stButton>button { width: 100% !important; background: transparent !important; border: 0.5px solid #444 !important; color: #ff4b4b !important; height: 18px !important; font-size: 10px !important; padding: 0 !important; margin-top: 2px !important; }
</style>
""", unsafe_allow_html=True)

def notify(tk, ci, msg):
    if tk and ci:
        try: requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", json={"chat_id":ci, "text":msg}, timeout=5)
        except: pass

with st.sidebar:
    st.header("⚙️ Admin")
    with st.expander("➕ Grup"):
        gn, tk, ci = st.text_input("Grup"), st.text_input("Token"), st.text_input("ChatID")
        if st.button("Simpan"):
            if gn and tk:
                db["groups"][gn] = {"tk": tk, "ci": ci, "members": {}}
                if tk not in db["h_tk"]: db["h_tk"].append(tk)
                save(db); st.rerun()
    if db["groups"]:
        target = st.selectbox("Grup", list(db["groups"].keys()))
        uid = st.text_input("ID Roblox")
        if st.button("Tambah"):
            if uid.isdigit():
                try:
                    res = requests.get(f"https://users.roblox.com/v1/users/{uid}", headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
                    if res.status_code == 200:
                        db["groups"][target]["members"][uid] = {"name": res.json().get("name", uid), "last": -1}
                        if uid not in db["h_id"]: db["h_id"].append(uid)
                        save(db); st.rerun()
                except: st.error("Error")
    with st.expander("👥 Riwayat"):
        for hid in db["h_id"]:
            c1, c2 = st.columns([3,1])
            c1.text(hid)
            if c2.button("❌", key=f"h{hid}"):
                db["h_id"].remove(hid); save(db); st.rerun()

st.title("Monitor 16:10")
for gn, info in db["groups"].items():
    if not info["members"]: continue
    st.subheader(f"📍 {gn}")
    uids = list(info["members"].keys())
    try:
        r = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}, timeout=10).json()
        pres = {str(p['userId']): p['userPresenceType'] for p in r.get('userPresences', [])}
        cols = st.columns(4)
        for i, uid in enumerate(uids):
            m = info["members"][uid]; cur = pres.get(uid, 0)
            if m.get("last") == 2 and cur != 2 and m.get("last") != -1:
                notify(info["tk"], info["ci"], f"🔴 {m['name']} KELUAR")
            db["groups"][gn]["members"][uid]["last"] = cur
            save(db)
            with cols[i % 4]:
                st.markdown(f'<div class="card"><div class="u-n"><span class="dot {"on" if cur==2 else "off"}"></span>{m["name"]}</div><div class="u-i">{uid}</div></div>', unsafe_allow_html=True)
                if st.button("🗑️", key=f"d{gn}{uid}"):
                    del db["groups"][gn]["members"][uid]; save(db); st.rerun()
    except: pass

time.sleep(15)
st.rerun()
