import streamlit as st
import requests
import time
import json

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Roblox Monitor Pro", layout="wide")

# CSS UNTUK STABILITAS VISUAL
st.markdown("""
    <style>
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 10px !important;
        justify-content: flex-start !important;
    }
    [data-testid="column"] {
        flex: 0 0 calc(25% - 15px) !important;
        min-width: 150px !important;
        max-width: calc(25% - 15px) !important;
        margin-bottom: 15px !important;
    }
    .card-roblox {
        border: 1px solid #444;
        border-radius: 10px;
        background-color: #1a1c24;
        padding: 15px;
        aspect-ratio: 16 / 10;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }
    .user-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        width: 100%;
        margin-bottom: 5px;
    }
    .status-dot {
        height: 12px;
        width: 12px;
        border-radius: 50%;
    }
    .online { background-color: #2ecc71; box-shadow: 0 0 8px #2ecc71; }
    .offline { background-color: #e74c3c; }
    .username-text {
        font-size: 14px;
        font-weight: bold;
        color: white;
    }
    .id-text { font-size: 11px; color: #888; }
    </style>
    """, unsafe_allow_html=True)

def send_telegram(token, chat_id, message):
    if not token or not chat_id: return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=5)
    except: pass

# --- INISIALISASI DATABASE (SESSION STATE) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "groups": {
            "Utama": {
                "token": "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k", 
                "chat_id": "8170247984", 
                "members": {}
            }
        },
        "h_id": [], 
        "h_tk": ["8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k"], 
        "h_ci": ["8170247984"]
    }

db = st.session_state.db

# --- SIDEBAR (ADMIN PANEL) ---
with st.sidebar:
    st.title("⚙️ Admin Panel")
    
    # 1. Fitur Backup & Restore
    with st.expander("💾 Backup & Restore (Anti Hilang)"):
        st.write("Simpan kode ini untuk cadangan:")
        st.code(json.dumps(db))
        restore_input = st.text_area("Tempel kode cadangan di sini:")
        if st.button("Restore Sekarang"):
            try:
                st.session_state.db = json.loads(restore_input)
                st.rerun()
            except:
                st.error("Kode tidak valid!")

    # 2. Set Bot & Grup
    with st.expander("🤖 Set Bot & Grup"):
        new_gname = st.text_input("Nama Grup Baru:")
        tk_sel = st.selectbox("Riwayat Token:", db["h_tk"])
        tk_new = st.text_input("Atau Token Baru:")
        ci_sel = st.selectbox("Riwayat Chat ID:", db["h_ci"])
        ci_new = st.text_input("Atau Chat ID Baru:")
        
        if st.button("Simpan Grup"):
            if new_gname:
                final_tk = tk_new if tk_new else tk_sel
                final_ci = ci_new if ci_new else ci_sel
                db["groups"][new_gname] = {"token": final_tk, "chat_id": final_ci, "members": {}}
                if final_tk not in db["h_tk"]: db["h_tk"].append(final_tk)
                if final_ci not in db["h_ci"]: db["h_ci"].append(final_ci)
                st.rerun()

    st.divider()
    
    # 3. Tambah Akun
    st.subheader("➕ Tambah Akun")
    target_grp = st.selectbox("Pilih Grup:", list(db["groups"].keys()))
    user_id = st.text_input("Masukkan ID Roblox:")
    
    if st.button("Tambahkan"):
        if user_id.isdigit():
            try:
                res = requests.get(f"https://users.roblox.com/v1/users/{user_id}").json()
                u_name = res.get('name', f"User-{user_id}")
                db["groups"][target_grp]["members"][user_id] = {"name": u_name, "last": 0}
                if user_id not in db["h_id"]: db["h_id"].append(user_id)
                st.success(f"Berhasil menambah {u_name}")
                st.rerun()
            except:
                st.error("ID tidak ditemukan")

# --- MONITORING UTAMA ---
st.header("🎮 Monitoring Center")

for g_name, g_data in db["groups"].items():
    st.subheader(f"📍 Grup: {g_name}")
    
    if not g_data["members"]:
        st.info(f"Belum ada akun di grup {g_name}")
        continue

    uids = list(g_data["members"].keys())
    
    try:
        # Fetch status roblox
        r = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}, timeout=5).json()
        pres_map = {str(p['userId']): p['userPresenceType'] for p in r.get('userPresences', [])}
        
        cols = st.columns(4)
        for i, uid in enumerate(uids):
            u_info = g_data["members"][uid]
            current_status = pres_map.get(uid, 0)
            
            # Notifikasi Telegram jika Status Berubah
            if u_info["last"] == 2 and current_status != 2:
                send_telegram(g_data["token"], g_data["chat_id"], f"🔴 {u_info['name']} telah KELUAR GAME")
            elif u_info["last"] != 2 and current_status == 2:
                send_telegram(g_data["token"], g_data["chat_id"], f"🟢 {u_info['name']} sedang MAIN GAME")
            
            # Update status terakhir
            db["groups"][g_name]["members"][uid]["last"] = current_status
            
            dot_class = "online" if current_status == 2 else "offline"
            
            with cols[i % 4]:
                st.markdown(f"""
                <div class="card-roblox">
                    <div class="
