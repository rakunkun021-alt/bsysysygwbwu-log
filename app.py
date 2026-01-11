import streamlit as st
import requests, time, json, os

# --- DATABASE ---
DB = "monitor_db.json"
def load():
    if os.path.exists(DB):
        try:
            with open(DB, "r") as f: return json.load(f)
        except: return {"groups":{}, "h_id":[]}
    return {"groups":{}, "h_id":[]}

def save(d):
    with open(DB, "w") as f: json.dump(d, f)

if 'db' not in st.session_state: st.session_state.db = load()
db = st.session_state.db

# --- UI CONFIG ---
st.set_page_config(page_title="Monitor", layout="wide")
st.markdown("""
<style>
    .block-container { padding: 0.5rem !important; }
    [data-testid="stHorizontalBlock"] { display: flex !important; gap: 2px !important; flex-wrap: nowrap !important; }
    [data-testid="column"] { flex: 1 1 25% !important; min-width: 0 !important; }
    .list-item { display: flex; align-items: center; border: 1px solid #333; background: #1e1e1e; padding: 2px 5px; border-radius: 2px; height: 26px; }
    .dot { height: 7px; width: 7px; border-radius: 50%; display: inline-block; margin-right: 5px; }
    .on { background: #0f0; box-shadow: 0 0 4px #0f0; }
    .off { background: #f00; }
    .u-n { font-size: 9px; font-weight: bold; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .stButton>button { background: transparent !important; border: none !important; color: #f44 !important; font-size: 14px !important; height: 26px !important; width: 100% !important; padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

def notify(tk, ci, msg):
    if tk and ci:
        try: requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", json={"chat_id":ci,"text":msg}, timeout=5)
        except: pass

# --- SIDEBAR ADMIN ---
with st.sidebar:
    st.header("Admin")
    with st.expander("Grup", expanded=True):
        gn = st.text_input("Nama")
        tk = st.text_input("Token")
        ci = st.text_input("ChatID")
        if st.button("Simpan Grup"):
            if gn and tk and ci:
                db["groups"][gn] = {"tk":tk, "ci":ci, "members":{}}
                save(db); st.rerun()
    
    if db["groups"]:
        st.divider()
        target = st.selectbox("Pilih Grup", list(db["groups"].keys()))
        uid = st.text_input("ID Roblox")
        if st.button("Tambah ID"):
            if uid.isdigit():
                try:
                    h = {"User-Agent": "Mozilla/5.0"}
                    r = requests.get(f"https://users.roblox.com/v1/users/{uid}", headers=h, timeout=10)
                    if r.status_code == 200:
                        db["groups"][target]["members"][uid] = {"name": r.json().get("name", uid), "last":-1}
                        if uid not in db["h_id"]: db["h_id"].append(uid)
                        save(db); st.rerun()
                except: st.error("API Error")

# --- DASHBOARD UTAMA ---
st.title("Roblox Monitor")
if not db["groups"]:
    st.info("Grup belum ada. Isi data di Sidebar lalu klik 'Simpan Grup'.")

for gn, info in db["groups"].items():
    with st.expander(gn, expanded=True):
        m_list = info.get("members", {})
        if not m_list:
            st.caption("Grup kosong. Tambah ID di Sidebar.")
            continue
            
        uids = list(m_list.keys())
        try:
            res = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds":uids}, timeout=10).json()
            pres = {str(p['userId']): p['userPresenceType'] for p in res.get('userPresences', [])}
            
            for j in range(0, len(uids), 4):
                cols = st.columns(4)
                for i, u_id in enumerate(uids[j:j+4]):
                    m = m_list[u_id]
                    cur = pres.get(u_id, 0)
                    # Logika Notif Keluar
                    if m.get("last") == 2 and cur != 2 and m.get("last") != -1:
                        notify(info["tk"], info["ci"], f"🔴 {m['name']} KELUAR")
                    
                    db["groups"][gn]["members"][u_id]["last"] = cur
                    save(db)
                    
                    with cols[i]:
                        c_l, c_r = st.columns([5,1])
                        c_l.markdown(f'<div class="list-item"><span class="dot {"on" if cur==2 else "off"}"></span><span class="u-n">{m["name"]}</span></div>', unsafe_allow_html=True)
                        if c_r.button("🗑️", key=f"d{gn}{u_id}"):
                            del db["groups"][gn]["members"][u_id]; save(db); st.rerun()
        except:
            st.error("Gagal update status")

time.sleep(15)
st.rerun()
