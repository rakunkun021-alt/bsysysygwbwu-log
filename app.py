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

# --- CONFIG & CSS (KUNCI 4 KOLOM & 16:10) ---
st.set_page_config(page_title="Roblox Monitor", layout="wide")
st.markdown("""
<style>
    /* Paksa kolom menyamping di mobile */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important; /* Kunci satu baris */
        gap: 5px !important;
        overflow-x: auto;
    }
    /* Lebar kolom pas 4 per baris */
    [data-testid="column"] {
        width: 24% !important;
        flex: 0 0 24% !important;
        min-width: 80px !important;
    }
    /* Box 16:10 Sesuai Request */
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
    .dot { height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-right: 4px; }
    .on { background: #2ecc71; box-shadow: 0 0 8px #2ecc71; }
    .off { background: #e74c3c; }
    .u-n { font-size: 11px; font-weight: bold; color: white; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 95%; }
    .u-i { font-size: 9px; color: #888; }
    /* Tombol Hapus tipis di bawah */
    .stButton>button {
        width: 100% !important;
        height: 20px !important;
        font-size: 8px !important;
        padding: 0 !important;
        margin-top: 2px !important;
    }
</style>
""", unsafe_allow_html=True)

def send_tg(tk, ci, msg):
    try: requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", json={"chat_id":ci, "text":msg}, timeout=5)
    except: pass

# --- SIDEBAR: MANAGEMENT ---
with st.sidebar:
    st.header("⚙️ Admin")
    
    with st.expander("➕ Tambah Grup"):
        gn = st.text_input("Nama Grup")
        tk = st.text_input("Token Bot")
        ci = st.text_input("Chat ID")
        if st.button("Simpan Grup Baru"):
            if gn and tk:
                db["groups"][gn] = {"tk": tk, "ci": ci, "members": {}}
                if tk not in db["h_tk"]: db["h_tk"].append(tk)
                save_db(db); st.rerun()

    if db["h_tk"]:
        with st.expander("📜 Riwayat Token"):
            for t in db["h_tk"]:
                st.code(t[:15]+"...")
                if st.button("Hapus", key=f"dtk_{t}"):
                    db["h_tk"].remove(t); save_db(db); st.rerun()

    st.divider()
    
    if db["groups"]:
        target = st.selectbox("Pilih Grup", list(db["groups"].keys()))
        uid = st.text_input("Input ID Roblox")
        if st.button("Tambah ID"):
            if uid.isdigit():
                try:
                    res = requests.get(f"https://users.roblox.com/v1/users/{uid}").json()
                    db["groups"][target]["members"][uid] = {"name": res.get("name", uid), "last": -1}
                    if uid not in db["h_id"]: db["h_id"].append(uid)
                    save_db(db); st.rerun()
                except: st.error("ID tidak valid")

    with st.expander("👥 Riwayat ID"):
        for hid in db["h_id"]:
            c1, c2 = st.columns([3,1])
            c1.text(hid)
            if c2.button("❌", key=f"hid_{hid}"):
                db["h_id"].remove(hid); save_db(db); st.rerun()

# --- MONITORING ---
st.title("Roblox Monitor 16:10")

if not db["groups"]:
    st.warning("Silakan tambah Grup terlebih dahulu di menu Sidebar sebelah kiri.")
else:
    for gn, info in db["groups"].items():
        st.subheader(f"📍 {gn}")
        if not info["members"]:
            st.info(f"Grup {gn} kosong. Tambahkan ID dari sidebar.")
            continue
            
        uids = list(info["members"].keys())
        try:
            r = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}, timeout=5).json()
            pres = {str(p['userId']): p['userPresenceType'] for p in r.get('userPresences', [])}
            
            # Kunci 4 Kolom
            cols = st.columns(4)
            for i, uid in enumerate(uids):
                m = info["members"][uid]
                cur = pres.get(uid, 0)
                
                # ALERT KELUAR GAME
                if m.get("last") == 2 and cur != 2 and m.get("last") != -1:
                    send_tg(info["tk"], info["ci"], f"🔴 {m['name']} KELUAR GAME")
                
                db["groups"][gn]["members"][uid]["last"] = cur
                save_db(db)
                
                with cols[i % 4]:
                    st.markdown(f"""
                    <div class="card">
                        <div class="u-n">
                            <span class="dot {'on' if cur==2 else 'off'}"></span>{m['name']}
                        </div>
                        <div class="u-i">{uid}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Hapus {uid}", key=f"del_{gn}_{uid}"):
                        del db["groups"][gn]["members"][uid]
                        save_db(db); st.rerun()
        except: pass

time.sleep(15)
st.rerun()
