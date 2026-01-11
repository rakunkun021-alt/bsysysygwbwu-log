import streamlit as st
import requests, time, json, os

# --- DATABASE PERMANEN ---
DB_FILE = "monitor_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {"groups": {}, "h_tk": [], "h_id": []}
    return {"groups": {}, "h_tk": [], "h_id": []}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

if 'db' not in st.session_state:
    st.session_state.db = load_db()
db = st.session_state.db

# --- CONFIG & CSS (4 KOLOM & 16:10 TETAP) ---
st.set_page_config(page_title="Roblox Monitor", layout="wide")
st.markdown("""
<style>
    /* Memaksa 4 kolom menyamping di semua device */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 6px !important;
    }
    [data-testid="column"] {
        width: calc(25% - 6px) !important;
        flex: 0 0 calc(25% - 6px) !important;
        min-width: calc(25% - 6px) !important;
        margin-bottom: 8px !important;
    }
    .card {
        border: 1px solid #444;
        border-radius: 8px;
        background: #1a1c24;
        aspect-ratio: 16 / 10;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 5px;
    }
    .dot { height: 9px; width: 9px; border-radius: 50%; display: inline-block; margin-right: 4px; }
    .on { background: #2ecc71; box-shadow: 0 0 8px #2ecc71; }
    .off { background: #e74c3c; }
    .u-n { font-size: 11px; font-weight: bold; color: white; overflow: hidden; text-overflow: ellipsis; width: 90%; white-space: nowrap; }
    .u-i { font-size: 9px; color: #888; }
    /* Tombol Tong Sampah */
    .stButton>button {
        width: 100% !important;
        background: transparent !important;
        border: 1px solid #444 !important;
        color: #ff4b4b !important;
        height: 24px !important;
        padding: 0 !important;
        margin-top: 3px !important;
    }
</style>
""", unsafe_allow_html=True)

def send_tg(tk, ci, msg):
    if tk and ci:
        try: requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", json={"chat_id":ci, "text":msg}, timeout=5)
        except: pass

# --- SIDEBAR MANAGEMENT ---
with st.sidebar:
    st.header("⚙️ Admin")
    with st.expander("➕ Tambah Grup"):
        gn = st.text_input("Nama Grup")
        tk = st.text_input("Token Bot")
        ci = st.text_input("Chat ID")
        if st.button("Simpan Grup"):
            if gn and tk:
                db["groups"][gn] = {"tk": tk, "ci": ci, "members": {}}
                if tk not in db["h_tk"]: db["h_tk"].append(tk)
                save_db(db); st.rerun()

    if db["h_tk"]:
        with st.expander("📜 Riwayat Token"):
            for t in db["h_tk"]:
                st.code(t[:15]+"...")
                if st.button("Hapus Token", key=f"dtk_{t}"):
                    db["h_tk"].remove(t); save_db(db); st.rerun()

    st.divider()
    if db["groups"]:
        target = st.selectbox("Pilih Grup", list(db["groups"].keys()))
        uid_in = st.text_input("Input ID Roblox")
        if st.button("Tambah ID"):
            if uid_in.isdigit():
                try:
                    res = requests.get(f"https://users.roblox.com/v1/users/{uid_in}", timeout=5)
                    if res.status_code == 200:
                        db["groups"][target]["members"][uid_in] = {"name": res.json().get("name", uid_in), "last": -1}
                        if uid_in not in db["h_id"]: db["h_id"].append(uid_in)
                        save_db(db); st.rerun()
                    else: st.error("ID Tidak Ada")
                except: st.error("API Error")

    with st.expander("👥 Riwayat ID"):
        for hid in db["h_id"]:
            c1, c2 = st.columns([3,1])
            c1.text(hid)
            if c2.button("❌", key=f"hid_{hid}"):
                db["h_id"].remove(hid); save_db(db); st.rerun()

# --- MONITORING ---
st.title("Roblox Monitor 16:10")

for gn, info in db["groups"].items():
    if not info["members"]: continue
    st.subheader(f"📍 {gn}")
    uids = list(info["members"].keys())
    try:
        r = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}, timeout=5).json()
        pres = {str(p['userId']): p['userPresenceType'] for p in r.get('userPresences', [])}
        
        cols = st.columns(4)
        for i, uid in enumerate(uids):
            m = info["members"][uid]
            cur = pres.get(uid, 0)
            
            # ALERT KELUAR GAME SAJA
            if m.get("last") == 2 and cur != 2 and m.get("last") != -1:
                send_tg(info["tk"], info["ci"], f"🔴 {m['name']} KELUAR GAME")
            
            db["groups"][gn]["members"][uid]["last"] = cur
            save_db(db)
            
            with cols[i % 4]:
                st.markdown(f"""
                <div class="card">
                    <div class="u-n"><span class="dot {'on' if cur==2 else 'off'}"></span>{m['name']}</div>
                    <div class="u-i">{uid}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{gn}_{uid}"):
                    del db["groups"][gn]["members"][uid]; save_db(db); st.rerun()
    except: pass

time.sleep(15)
st.rerun()
