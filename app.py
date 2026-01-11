import streamlit as st
import requests
import time

# --- FUNGSI KIRIM TELEGRAM ---
def send_telegram(token, chat_id, message):
    if not token or not chat_id:
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=5)
    except:
        pass

# Setup Halaman
# Pastikan baris ini ada 'layout="wide"'
st.set_page_config(page_title="Roblox Multi-Group", page_icon="🎮", layout="wide", initial_sidebar_state="expanded")st.set_page_config(page_title="Roblox Multi-Group", page_icon="🎮", layout="wide", initial_sidebar_state="expanded")
st.title("📱 Roblox Group Monitor")

# --- SISTEM PENYIMPANAN DATA ---
@st.cache_resource
def get_global_data():
    return {
        "groups": {
            "Utama": {
                "token": "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k",
                "chat_id": "8170247984",
                "members": {} 
            }
        },
        "history": []
    }

db = get_global_data()

def get_username(uid):
    try:
        res = requests.get(f"https://users.roblox.com/v1/users/{uid}").json()
        return res.get('name', f"User-{uid}")
    except:
        return f"User-{uid}"

# --- SIDEBAR: KONFIGURASI GRUP & BOT ---
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    
    # 1. Fitur Tambah Grup & Bot Baru
    with st.expander("➕ Tambah Grup / Bot Baru"):
        new_g_name = st.text_input("Nama Grup (Misal: Server 1):")
        g_token = st.text_input("Bot Token Baru (Opsional):")
        g_chatid = st.text_input("Chat ID Baru (Opsional):")
        if st.button("Buat Grup"):
            if new_g_name and new_g_name not in db["groups"]:
                db["groups"][new_g_name] = {
                    "token": g_token if g_token else db["groups"]["Utama"]["token"],
                    "chat_id": g_chatid if g_chatid else db["groups"]["Utama"]["chat_id"],
                    "members": {}
                }
                st.success(f"Grup {new_g_name} Aktif!")
                st.rerun()

    st.divider()
    
    # 2. Fitur Tambah ID ke Grup
    st.subheader("👤 Tambah Akun")
    target_group = st.selectbox("Pilih Grup:", list(db["groups"].keys()))
    new_id = st.text_input("User ID Roblox:", placeholder="Masukkan angka...")
    
    if st.button("Simpan ke Grup"):
        if new_id.isdigit():
            uid = int(new_id)
            if uid not in db["groups"][target_group]["members"]:
                name = get_username(uid)
                db["groups"][target_group]["members"][uid] = {"name": name, "last_status": -1}
                st.success(f"{name} ditambah ke {target_group}")
                st.rerun()

    st.divider()
    if st.button("🔴 Reset Semua Data"):
        db["groups"] = {"Utama": db["groups"]["Utama"]}
        db["groups"]["Utama"]["members"] = {}
        st.rerun()

# --- HALAMAN UTAMA: TAMPILAN 4 ID PER BARIS ---
for g_name, g_data in db["groups"].items():
    if not g_data["members"]:
        continue
        
    st.subheader(f"📍 Grup: {g_name}")
    uids = list(g_data["members"].keys())
    
    try:
        # Cek status ke Roblox
        res = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}).json()
        presences = {p['userId']: p['userPresenceType'] for p in res.get('userPresences', [])}
        
        # Fitur 1 Baris = 4 ID (Grid)
        rows = [uids[i:i + 4] for i in range(0, len(uids), 4)]
        
        for row in rows:
            cols = st.columns(4)
            for i, uid in enumerate(row):
                current_status = presences.get(uid, 0)
                old_status = g_data["members"][uid]["last_status"]
                name = g_data["members"][uid]["name"]
                
                # Notifikasi Keluar (sesuai Bot Grup masing-masing)
                if old_status == 2 and current_status != 2:
                    send_telegram(g_data["token"], g_data["chat_id"], f"🔴 [{g_name}] {name} Keluar Game")
                
                db["groups"][g_name]["members"][uid]["last_status"] = current_status
                
                # Tampilan Kotak ID
                with cols[i]:
                    with st.container(border=True):
                        color = "🟢" if current_status == 2 else "🔴"
                        st.markdown(f"**{color} {name}**")
                        st.caption(f"ID: {uid}")
                        if st.button("Hapus", key=f"del_{g_name}_{uid}"):
                            del db["groups"][g_name]["members"][uid]
                            st.rerun()
        st.divider()
    except:
        st.error(f"Gagal memuat grup {g_name}")

# Auto Refresh
time.sleep(30)
st.rerun()
