import streamlit as st
import requests
import time
import json

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Roblox Monitor Pro", layout="wide")

# CSS UNTUK GRID 4 KOLOM & INDIKATOR SAMPING NAMA
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
        border-radius: 8px;
        background-color: #1a1c24;
        padding: 12px;
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
    }
    .status-dot {
        height: 12px;
        width: 12px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .online { background-color: #2ecc71; box-shadow: 0 0 8px #2ecc71; }
    .offline { background-color: #e74c3c; }
    .username-text {
        font-size: 13px;
        font-weight: bold;
        color: white;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .id-text { font-size: 10px; color: #888; margin-top: 4px; }
    .stButton > button {
        width: 100% !important;
        height: 26px !important;
        font-size: 11px !important;
        padding: 0px !important;
        margin-top: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

def send_telegram(token, chat_id, message):
    if not token or not chat_id:
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        requests.post(url, json=payload, timeout=5)
    except:
        pass

# --- DATABASE SESSION ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "groups": {"Utama": {"token": "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k", "chat_id": "8170247984", "members": {}}},
        "h_id": [], 
        "h_tk": ["8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k"], 
        "h_ci": ["8170247984"]
    }

db = st.session_state.db

# --- SIDEBAR (ADMIN PANEL) ---
with st.sidebar:
    st.header("⚙️ Admin Panel")
    
    # Fitur Anti-Hilang
    with st.expander("💾 Backup & Restore (Anti Hilang)"):
        st.write("Salin kode ini ke Catatan HP:")
        st.code(json.dumps(db))
        restore_code = st.text_area("Tempel kode restore di sini:")
        if st.button("Restore Sekarang"):
            try:
                st.session_state.db = json.loads(restore_code)
                st.rerun()
            except: 
                st.error("Kode tidak valid!")

    # Fitur Set Bot & Grup
    with st.expander("🤖 Set Bot & Grup"):
        gn = st.text_input("Nama Grup Baru:")
        tk_s = st.selectbox("Riwayat Token:", db["h_tk"])
        tk_n = st.text_input("Atau Token Baru:")
        ci_s = st.selectbox("Riwayat Chat ID:", db["h_ci"])
        ci_n = st.text_input("Atau Chat ID Baru:")
        if st.button("Simpan Grup"):
            if gn:
                ft = tk_n if tk_n else tk_s
                fc = ci_n if ci_n else ci_s
                db["groups"][gn] = {"token": ft, "chat_id": fc, "members": {}}
                if ft and ft not in db["h_tk"]: db["h_tk"].append(ft)
                if fc and fc not in db["h_ci"]: db["h_ci"].append(fc)
                st.rerun()

    st.divider()
    
    # Fitur Tambah Akun
    st.subheader("➕ Tambah Akun")
    target = st.selectbox("Pilih Grup:", list(db["groups"].keys()))
    h_sel = st.selectbox("Riwayat ID:", ["-- Baru --"] + db["h_id"])
    u_in = st.text_input("ID Roblox:", value="" if h_sel == "-- Baru --" else h_sel)
    
    if st.button("Tambahkan"):
        if u_in.isdigit():
            try:
                res = requests.get(f"https://users.roblox.com/v1/users/{u_in}").json()
                name = res.get('name', f"User-{u_in}")
                db["groups"][target]["members"][u_in] = {"name": name, "last": 0}
                if u_in not in db["h_id"]: db["h_id"].append(u_in)
                st.rerun()
            except: 
                st.error("Gagal menambah ID")

# --- MONITORING UTAMA ---
st.title("Roblox Live Monitor")

for g_name, g_data in db["groups"].items():
    st.subheader(f"📍 Grup: {g_name}")
    if not g_data["members"]:
        st.info("Grup ini masih kosong.")
        continue
    
    uids = list(g_data["members"].keys())
    try:
        r = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}, timeout=5).json()
        pres = {str(p['userId']): p['userPresenceType'] for p in r.get('userPresences', [])}
        
        cols = st.columns(4)
        for i, uid in enumerate(uids):
            info = g_data["members"][uid]
            curr = pres.get(uid, 0)
            
            # Cek Perubahan Status (Telegram)
            if info["last"] == 2 and curr != 2:
                send_telegram(g_data["token"], g_data["chat_id"], f"🔴 {info['name']} Keluar Game")
            elif info["last"] != 2 and curr == 2:
                send_telegram(g_data["token"], g_data["chat_id"], f"🟢 {info['name']} Masuk Game")
            
            db["groups"][g_name]["members"][uid]["last"] = curr
            dot = "online" if curr == 2 else "offline"
            
            with cols[i % 4]:
                st.markdown(f"""
                <div class="card-roblox">
                    <div class="user-row">
                        <div class="status-dot {dot}"></div>
                        <div class="username-text">{info['name']}</div>
                    </div>
                    <div class="id-text">{uid}</div>
                </div>
                """, unsafe_allow_html=True)
                # Tombol Hapus per akun
                if st.button(f"Hapus {uid}", key=f"del_{g_name}_{uid}"):
                    del db["groups"][g_name]["members"][uid]
                    st.rerun()
    except:
        st.write("Sedang memperbarui data...")

time.sleep(20)
st.rerun()
