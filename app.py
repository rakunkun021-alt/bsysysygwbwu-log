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

st.set_page_config(page_title="Roblox Monitor", layout="wide")
st.markdown('<style>.block-container{padding:0.5rem!important;} .stButton>button{width:100%!important; white-space:nowrap!important;} .dot{height:10px; width:10px; border-radius:50%; display:inline-block; margin-right:8px;} .on{background:#0f0; box-shadow:0 0 10px #0f0;} .off{background:#f00;} .list-row{display:flex; align-items:center; background:#1e1e1e; border:1px solid #333; padding:8px; border-radius:5px; margin-bottom:2px; flex-grow:1;} .main-title{background: linear-gradient(90deg, #ff4b4b, #ff8181); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 32px; font-weight: bold; text-align: center; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 2px; border-bottom: 2px solid #333; padding-bottom: 10px;}</style>', unsafe_allow_html=True)

def notify(tk, ci, msg):
    try: requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", json={"chat_id":ci,"text":msg}, timeout=8)
    except: pass

with st.sidebar:
    st.header("⚙️ ADMIN PANEL")
    with st.expander("➕ GRUP BARU", expanded=False):
        gn, tk, ci = st.text_input("Nama Grup"), st.text_input("Token Bot"), st.text_input("Chat ID")
        if st.button("SIMPAN GRUP"):
            if gn and tk and ci:
                db["groups"][gn] = {"tk":tk, "ci":ci, "members":{}}
                save(db); st.rerun()
    
    if db["groups"]:
        st.write("---")
        target = st.selectbox("Pilih Grup Tujuan", list(db["groups"].keys()))
        uids_input = st.text_area("Tambah ID Massal", placeholder="Contoh: 12345, 67890, 54321")
        st.caption("Gunakan koma (,) untuk memisahkan banyak ID.")
        
        if st.button("TAMBAH SEMUA ID"):
            if uids_input:
                id_list = [x.strip() for x in uids_input.replace("\n", ",").split(",") if x.strip().isdigit()]
                for uid in id_list:
                    try:
                        r = requests.get(f"https://users.roblox.com/v1/users/{uid}", headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
                        if r.status_code == 200:
                            name = r.json().get("name", uid)
                            db["groups"][target]["members"][uid] = {"name": name, "last": -1}
                            if uid not in db["h_id"]: db["h_id"].append(uid)
                    except: pass
                save(db); st.success(f"Berhasil memproses {len(id_list)} ID"); time.sleep(1); st.rerun()

    with st.expander("📜 RIWAYAT ID"):
        for hid in db.get("h_id", []):
            c1, c2 = st.columns([3,1])
            c1.caption(hid)
            if c2.button("❌", key="h"+hid):
                db["h_id"].remove(hid); save(db); st.rerun()

# Judul Baru yang Menarik
st.markdown('<div class="main-title">ROBLOX ONLINE LOGGING</div>', unsafe_allow_html=True)

for gn, info in db["groups"].items():
    with st.expander(f"📍 {gn.upper()}", expanded=True):
        m_list = info.get("members", {})
        if not m_list:
            st.caption("Belum ada ID di grup ini.")
            continue
        
        uids = list(m_list.keys())
        try:
            res = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds":[int(x) for x in uids]}, timeout=10).json()
            pres = {str(p['userId']): p['userPresenceType'] for p in res.get('userPresences', [])}
            
            for u_id in uids:
                m = m_list[u_id]; cur = pres.get(u_id, 0)
                if m.get("last") == 2 and cur != 2:
                    notify(info["tk"], info["ci"], f"🔴 {m['name']} KELUAR GAME")
                
                db["groups"][gn]["members"][u_id]["last"] = cur
                save(db)
                
                cl, cr = st.columns([0.88, 0.12])
                with cl:
                    st.markdown(f'<div class="list-row"><span class="dot {"on" if cur==2 else "off"}"></span><b style="color:#fff;font-size:14px;">{m["name"]}</b> <span style="color:#888;font-size:12px;margin-left:5px;">({u_id})</span></div>', unsafe_allow_html=True)
                with cr:
                    if st.button("🗑️", key="del"+gn+u_id):
                        del db["groups"][gn]["members"][u_id]; save(db); st.rerun()
        except: pass

time.sleep(15)
st.rerun()
