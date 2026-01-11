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

# --- CONFIG & CSS (OPTIMASI VIEW IDENTIK DESKTOP & MOBILE) ---
st.set_page_config(page_title="Roblox Monitor", layout="wide")
st.markdown("""
<style>
    /* Memaksa tampilan kolom tetap menyamping (Grid) di semua perangkat */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important; /* Memungkinkan baris baru setelah 4 kolom */
        gap: 8px !important;
    }
    
    /* Memaksa lebar kolom menjadi 25% (4 kolom) baik di HP maupun Desktop */
    [data-testid="column"] {
        width: calc(25% - 8px) !important;
        flex: 0 0 calc(25% - 8px) !important;
        min-width: calc(25% - 8px) !important;
        margin-bottom: 10px !important;
    }

    /* Box Rasio 16:10 */
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
        position: relative;
    }
    
    .dot { height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-right: 4px; }
    .on { background: #2ecc71; box-shadow: 0 0 8px #2ecc71; }
    .off { background: #e74c3c; }
    
    .u-n { font-size: 11px; font-weight: bold; color: white; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 90%; }
    .u-i { font-size: 9px; color: #888; }

    /* Styling tombol tong sampah agar rapi di bawah card */
    .stButton>button {
        width: 100% !important;
        background-color: transparent !important;
        border: 1px solid #444 !important;
        color: #ff4b4b !important;
        height: 25px !important;
        padding: 0 !important;
        margin-top: 3px !important;
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
                if st.button("Hapus Token", key=f"dtk_{t}"):
                    db["h_tk"].remove(t); save_db(db); st.rerun()

    st.divider()
    
    if db["groups"]:
        target = st.selectbox("Pilih Grup", list(db["groups"].keys()))
        uid_input = st.text_input("Input ID Roblox", key="input_id")
        if st.button("Tambah ID"):
            if uid_input.isdigit():
                # Menghapus notifikasi error palsu dengan mencoba request terlebih dahulu
                try:
                    with st.spinner('Validasi ID...'):
                        res = requests.get(f"https://users.roblox.com/v1/users/{uid_input}", timeout=5)
                        if res.status_code == 200:
                            user_data = res.json()
                            db["groups"][target]["members"][uid_input] = {"name": user_data.get("name", uid_input), "last": -1}
                            if uid_input not in db["h_id"]: db["h_id"].append(uid_input)
                            save_db(db)
                            st.rerun()
                        else:
                            st.error("ID tidak ditemukan di Roblox")
                except:
                    st.error("Gagal terhubung ke API Roblox")
            else:
                st.warning("Masukkan angka saja")

    with st.expander("👥 Riwayat ID"):
        for hid in db["h_id"]:
            c1, c2 = st.columns([3,1])
            c1.text(hid)
            if c2.button("❌", key=f"hid_{hid}"):
                db["h_id"].remove(hid); save_db(db); st.rerun()

# --- MONITORING ---
st.title("Roblox Monitor 16:10")

if not db["groups"]:
    st.warning("Silakan tambah Grup terlebih dahulu di sidebar.")
else:
    for gn, info in db["groups"].items():
        st.subheader(f"📍 {gn}")
        if not info["members"]:
            continue
            
        uids = list(info["members"].keys())
        try:
            r = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}, timeout=5).json()
            pres = {str(p['userId']): p['userPresenceType'] for p in r.get('userPresences', [])}
            
            # Grid 4 Kolom (Berlaku untuk Desktop & Mobile)
            cols = st.columns(4)
            for i, uid in enumerate(uids):
                m = info["members"][uid]
                cur = pres.get(uid, 0)
                
                # ALERT KELUAR GAME
                if m.get("last") == 2 and cur != 2 and m.get("last") != -1:
                    send_tg(
