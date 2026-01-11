import streamlit as st
import requests, time, json

# --- CONFIG & CSS ---
st.set_page_config(page_title="Monitor 16:10", layout="wide")
st.markdown("""
<style>
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: wrap !important; gap: 8px !important; }
    [data-testid="column"] { width: calc(25% - 10px) !important; flex: 0 0 calc(25% - 10px) !important; min-width: calc(25% - 10px) !important; margin-bottom: 10px !important; }
    .card { border: 1px solid #444; border-radius: 8px; background: #1a1c24; padding: 10px 5px; aspect-ratio: 16 / 10; display: flex; flex-direction: column; justify-content: center; align-items: center; }
    .row { display: flex; align-items: center; gap: 6px; width: 100%; justify-content: center; }
    .dot { height: 10px; width: 10px; border-radius: 50%; flex-shrink: 0; }
    .on { background: #2ecc71; box-shadow: 0 0 5px #2ecc71; }
    .off { background: #e74c3c; }
    .u-text { font-size: 11px; font-weight: bold; color: white; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .id-t { font-size: 9px; color: #888; margin-top: 2px; }
    .stButton>button { width: 100% !important; height: 24px !important; font-size: 9px !important; padding: 0 !important; margin-top: 5px !important; }
</style>
""", unsafe_allow_html=True)

def send_tg(tk, ci, msg):
    if tk and ci:
        try: requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", json={"chat_id":ci, "text":msg}, timeout=5)
        except: pass

# --- DB SESSION ---
if 'db' not in st.session_state:
    st.session_state.db = {"groups": {"Utama": {"tk": "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k", "ci": "8170247984", "members": {}}}, "h_id": []}
db = st.session_state.db

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Admin")
    with st.expander("💾 Backup"):        if st.button("Restore"):
            try: st.session_state.db = json.loads(rc); st.rerun()
            except: st.error("Gagal")
    
    target = st.selectbox("Grup:", list(db["groups"].keys()))
    u_in = st.text_input("ID Roblox:")
    if st.button("Tambah"):
        if u_in.isdigit():
            try:
                res = requests.get(f"https://users.roblox.com/v1/users/{u_in}").json()
                db["groups"][target]["members"][u_in] = {"name": res.get('name', u_in), "last": -1}
                if u_in not in db["h_id"]: db["h_id"].append(u_in)
                st.rerun()
            except: st.error("Gagal")

# --- MONITORING ---
st.title("Roblox Monitor 16:10")
for gn, gd in db["groups"].items():
    if gd["members"]:
        st.subheader(f"📍 {gn}")
        uids = list(gd["members"].keys())
        try:
            r = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}, timeout=5).json()
            pres = {str(p['userId']): p['userPresenceType'] for p in r.get('userPresences', [])}
            cols = st.columns(4)
            for i, uid in enumerate(uids):
                inf = gd["members"][uid]
                cur = pres.get(uid, 0)
                # NOTIF KELUAR SAJA
                if inf["last"] == 2 and cur != 2 and inf["last"] != -1:
                    send_tg(gd["tk"], gd["ci"], f"🔴 {inf['name']} KELUAR GAME")
                db["groups"][gn]["members"][uid]["last"] = cur
                with cols[i % 4]:
                    st.markdown(f'<div class="card"><div class="row"><div class="dot {"on" if cur==2 else "off"}"></div><div class="u-text">{inf["name"]}</div></div><div class="id
