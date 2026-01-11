import streamlit as st
import requests, time, json, os

# --- DATABASE PERMANEN ---
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

# --- UI CONFIG (OPTIMASI MOBILE 4 KOLOM) ---
st.set_page_config(page_title="Roblox Monitor", layout="wide")
st.markdown("""
<style>
    .block-container { padding: 0.5rem !important; }
    /* Paksa 4 kolom tetap berjejer di mobile */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important;
    }
    [data-testid="column"] {
        flex: 1 1 25% !important;
        min-width: 0 !important;
    }
    .card {
        border: 1px solid #333;
        border-radius: 4px;
        background: #1e1e1e;
        aspect-ratio: 16 / 10;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 2px;
    }
    .dot { height: 6px; width: 6px; border-radius: 50%; display: inline-block; margin-right: 2px; }
    .on { background: #00ff00; box-shadow: 0 0 5px #00ff00; }
    .off { background: #ff0000; }
    .u-n { font-size: 8px; font-weight: bold; color: #fff; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; width: 90%; text-align: center; }
    .u-i { font-size: 6px; color: #aaa; }
    /* Tombol Sampah */
    .stButton > button {
        width: 100% !important;
        height: 18px !important;
        padding: 0 !important;
        font-size: 10px !important;
        background: transparent !important;
        border: 1px solid #444 !important;
        margin-top: 2px !important;
    }
</style>
""", unsafe_allow_html=True)

def notify(tk, ci, msg):
    if tk and ci:
        try: requests.post("https://api.telegram.org/bot" + tk + "/sendMessage", json={"chat_id":ci, "text":msg}, timeout=5)
        except: pass

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Admin")
    with st.expander("➕ Grup"):
        gn = st.text_input("Nama Grup")
        tk = st.text_input("Token Bot")
        ci = st.text_input("Chat ID")
        if st.button("Simpan Grup"):
            if gn and tk:
                db["groups"][gn] = {"tk": tk, "ci": ci, "members": {}}
                if tk not in db["h_tk"]: db["h_tk"].append(tk)
                save(db); st.rerun()

    if db["groups"]:
        st.divider()
        target = st.selectbox("Pilih Grup", list(db["groups"].keys()))
        uid = st.text_input("ID Roblox")
        if st.button("Tambah"):
            if uid.isdigit():
                # Gunakan User-Agent agar tidak diblokir Roblox
                h = {"User-Agent": "Mozilla/5.0"}
                try:
                    r = requests.get("https://users.roblox.com/v1/users/" + uid, headers=h, timeout=10)
                    if r.status_code == 200:
                        name = r.json().get("name", uid)
                        db["groups"][target]["members"][uid] = {"name": name, "last": -1}
                        if uid not in db["h_id"]: db["h_id"].append(uid)
                        save(db); st.rerun()
                    else:
                        st.warning("ID Tidak Terdaftar")
                except:
                    st.error("Koneksi API Gagal")

    with st.expander("👥 Riwayat ID"):
        for hid in db["h_id"]:
            c1, c2 = st.columns([3,1])
            c1.text(hid)
            if c2.button("❌", key="h"+hid):
                db["h_id"].remove(hid); save(db); st.rerun()

# --- MAIN DASHBOARD ---
st.title("Monitor 16:10")

if not db["groups"]:
    st.info("Tambahkan Grup di sidebar untuk memulai.")

for gn, info in db["groups"].items():
    # Fitur Minimize Grup
    with st.expander(gn, expanded=True):
        if not info["members"]:
            st.caption("Belum ada ID di grup ini.")
            continue
            
        uids = list(info["members"].keys())
        try:
            # Batch request presence
            res = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}, timeout=10).json()
            pres = {str(p['userId']): p['userPresenceType'] for p in res.get('userPresences', [])}
            
            # Buat baris (4 kolom)
            for j in range(0, len(uids), 4):
                batch = uids[j:j+4]
                cols = st.columns(4)
                for i, user_id in enumerate(batch):
                    m = info["members"][user_id]
