import streamlit as st
import requests, time, json, os

# --- DATABASE PERMANEN ---
DB = "monitor_db.json"

def load_data():
    if os.path.exists(DB):
        try:
            with open(DB, "r") as f:
                data = json.load(f)
                # Pastikan struktur data lengkap
                if "groups" not in data: data["groups"] = {}
                if "h_id" not in data: data["h_id"] = []
                if "tokens" not in data: data["tokens"] = {}
                return data
        except:
            return {"groups": {}, "h_id": [], "tokens": {}}
    return {"groups": {}, "h_id": [], "tokens": {}}

def save_data(data):
    with open(DB, "w") as f:
        json.dump(data, f, indent=4)

# Inisialisasi Data
if 'db' not in st.session_state:
    st.session_state.db = load_data()

db = st.session_state.db

# --- UI CONFIG ---
st.set_page_config(page_title="Roblox Monitor", layout="wide")
st.markdown("""
<style>
    .block-container { padding: 0.5rem !important; }
    /* Pastikan list turun ke bawah (1 kolom penuh) */
    [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
    
    .list-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #333;
        background: #1e1e1e;
        padding: 5px 10px;
        border-radius: 4px;
        margin-bottom: 5px;
        height: 35px;
    }
    .user-info { display: flex; align-items: center; gap: 8px; }
    .dot { height: 8px; width: 8px; border-radius: 50%; display: inline-block; }
    .on { background: #0f0; box-shadow: 0 0 5px #0f0; }
    .off { background: #f00; }
    .u-n { font-size: 11px; font-weight: bold; color: #fff; }
    
    /* Tombol Sampah Sejajar */
    .stButton>button {
        background: transparent !important;
        border: none !important;
        color: #ff4b4b !important;
        font-size: 16px !important;
        padding: 0 !important;
        width: 30px !important;
        height: 30px !important;
    }
</style>
""", unsafe_allow_html=True)

def notify(tk, ci, msg):
    if tk and ci:
        try:
            requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", 
                          json={"chat_id": ci, "text": msg}, timeout=5)
        except: pass

# --- SIDEBAR ADMIN ---
with st.sidebar:
    st.header("Admin")
    with st.expander("➕ Tambah/Edit Grup", expanded=False):
        gn = st.text_input("Nama Grup")
        tk = st.text_input("Token Bot")
        ci = st.text_input("Chat ID")
        if st.button("Simpan Grup"):
            if gn and tk and ci:
                db["groups"][gn] = {"tk": tk, "ci": ci, "members": {}}
                save_data(db)
                st.rerun()

    if db["groups"]:
        st.divider()
        target = st.selectbox("Pilih Grup", list(db["groups"].keys()))
        uid = st.text_input("Masukkan ID Roblox")
        if st.button("Tambah ke List"):
            if uid.isdigit():
                try:
                    h = {"User-Agent": "Mozilla/5.0"}
                    r = requests.get(f"https://users.roblox.com/v1/users/{uid}", headers=h, timeout=10)
                    if r.status_code == 200:
                        name = r.json().get("name", uid)
                        db["groups"][target]["members"][uid] = {"name": name, "last": -1}
                        if uid not in db["h_id"]: db["h_id"].append(uid)
                        save_data(db)
                        st.rerun()
                    else: st.error("ID tidak ditemukan")
                except: st.error("Koneksi API Roblox Gagal")

    with st.expander("📜 Riwayat ID"):
        for hid in db["h_id"]:
            c1, c2 = st.columns([4, 1])
            c1.caption(hid)
            if c2.button("❌", key=f"hist_{hid}"):
                db["h_id"].remove(hid)
                save_data(db); st.rerun()

# --- DASHBOARD UTAMA ---
st.title("Roblox Monitor")

if not db["groups"]:
    st.info("Gunakan Sidebar untuk menambah Grup dan Token.")

for gn, info in db["groups"].items():
    with st.expander(f"📍 {gn}", expanded=True):
        members = info.get("members", {})
        if not members:
            st.caption("Belum ada ID di grup ini.")
            continue
            
        uids = list(members.keys())
        try:
            # Batch request untuk efisiensi
            res = requests.post("https://presence.roblox.com/v1/presence/users", 
                                json={"userIds": [int(x) for x in uids]}, timeout=10)
            if res.status_code == 200:
                pres_data = res.json().get('userPresences', [])
                pres_dict = {str(p['userId']): p['userPresenceType'] for p in pres_data}
                
                # Render List (Kebawah)
                for user_id in uids:
                    m = members[user_id]
                    cur = pres_dict.get(user_id, 0)
                    
                    # Notifikasi jika keluar (2 = InGame)
                    if m.get("last") == 2 and cur != 2 and m.get("last") != -1:
                        notify(info["tk"], info["ci"], f"🔴 {m['name']} KELUAR GAME")
                    
                    db["groups"][gn]["members"][user_id]["last"] = cur
                    save_data(db)
                    
                    # Tampilan List Item Sejajar
                    col_item, col_del = st.columns([9, 1])
                    with col_item:
                        st.markdown(f'''
                            <div class="list-item">
                                <div class="user-info">
                                    <span class="dot {"on" if cur==2 else "off"}"></span>
                                    <span class="u-n">{m["name"]} ({user_id})</span>
                                </div>
                            </div>
                        ''', unsafe_allow_html=True)
                    with col_del:
                        if st.button("🗑️", key=f"del_{gn}_{user_id}"):
                            del db["groups"][gn]["members"][user_id]
                            save_data(db); st.rerun()
            else:
                st.warning("API Roblox sedang sibuk (Rate Limited)")
        except:
            st.error("Gagal update status")

# Auto Refresh
time.sleep(15)
st.rerun()
