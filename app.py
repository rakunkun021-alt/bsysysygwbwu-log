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

# --- UI CONFIG (RESOLUSI ULTRA KECIL UNTUK 4 KOLOM HP) ---
st.set_page_config(page_title="Monitor", layout="wide")
st.markdown("""
<style>
    .block-container { padding: 0.5rem !important; }
    /* Paksa Grid 4 Kolom di Mobile */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important; 
        gap: 3px !important;
    }
    [data-testid="column"] {
        width: 25% !important;
        flex: 1 1 25% !important;
        min-width: 0px !important;
    }
    /* Card 16:10 Resolusi Rendah */
    .card {
        border: 1px solid #444;
        border-radius: 4px;
        background: #1a1c24;
        aspect-ratio: 16 / 10;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 2px;
    }
    .dot { height: 5px; width: 5px; border-radius: 50%; display: inline-block; margin-right: 2px; }
    .on { background: #2ecc71; box-shadow: 0 0 3px #2ecc71; }
    .off { background: #e74c3c; }
    .u-n { font-size: 7px; font-weight: bold; color: white; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 95%; text-align: center; }
    .u-i { font-size: 5px; color: #888; text-align: center; }
    /* Tombol Sampah Kecil */
    .stButton>button {
        width: 100% !important;
        background: transparent !important;
        border: 0.5px solid #444 !important;
        color: #ff4b4b !important;
        height: 15px !important;
        font-size: 8px !important;
        padding: 0 !important;
        margin-top: 2px !important;
    }
</style>
""", unsafe_allow_html=True)

def notify(tk, ci, msg):
    if tk and ci:
        try: requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", json={"chat_id":ci, "text":msg}, timeout=5)
        except: pass

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Admin")
    with st.expander("➕ Tambah Grup"):
        gn, tk, ci = st.text_input("Grup"), st.text_input("Token"), st.text_input("ChatID")
        if st.button("Simpan"):
            if gn and tk:
                db["groups"][gn] = {"tk": tk, "ci": ci, "members": {}}
                if tk not in db["h_tk"]: db["h_tk"].append(tk)
                save(db); st.rerun()

    if db["groups"]:
        st.divider()
        target = st.selectbox("Pilih Grup", list(db["groups"].keys()))
        uid = st.text_input("Input ID Roblox")
        if st.button("Tambah ID"):
            if uid.isdigit():
                try:
                    res = requests.get(f"https://users.roblox.com/v1/users/{uid}", headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
                    if res.status_code == 200:
                        db["groups"][target]["members"][uid] = {"name": res.json().get("name", uid), "last": -1}
                        if uid not in db["h_id"]: db["h_id"].append(uid)
                        save(db); st.rerun()
                except: st.toast("API Error", icon="⚠️")

    with st.expander("👥 Riwayat ID"):
        for hid in db["h_id"]:
            c1, c2 = st.columns([3,1])
            c1.text(hid)
            if c2.button("❌", key=f"h{hid}"):
                db["h_id"].remove(hid); save(db); st.rerun()

# --- MAIN DASHBOARD ---
st.title("Monitor 16:10")

for gn, info in db["groups"].items():
    # FITUR MINIMIZE GRUP (Menggunakan Expander)
    with st.expander(f"📍 {gn}", expanded=True):
        if not info["members"]:
            st.write("Grup Kosong")
            continue
            
        uids = list(info["members"].keys())
        try:
            r = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}, timeout=10).json()
            pres = {str(p['userId']): p['userPresenceType'] for p in r.get('userPresences', [])}
            
            # Tampilan Grid 4 Kolom per Baris
            for j in range(0, len(uids), 4):
                batch = uids[j:j+4]
                cols = st.columns(4)
                for i, uid in enumerate(batch):
                    m = info["members"][uid]
                    cur = pres.get(uid, 0)
                    
                    if m.get("last") == 2 and cur != 2 and m.get("last") != -1:
                        notify(info["tk"], info["ci"], f"🔴 {m['name']} KELUAR")
                    
                    db["groups"][gn]["members"][uid]["last"] = cur
                    save(db)
                    
                    with cols[i]:
                        st.markdown(f"""
                        <div
