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

st.set_page_config(page_title="Roblox Multi-Server Monitor", page_icon="🎮", layout="wide")
st.title("📱 Roblox Group Monitor")

# --- SISTEM PENYIMPANAN ---
@st.cache_resource
def get_global_data():
    return {
        "groups": {
            "Default": {
                "token": "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k",
                "chat_id": "8170247984",
                "members": {} # {uid: {name: str, status: int}}
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

# --- SIDEBAR: MANAJEMEN GRUP & AKUN ---
with st.sidebar:
    st.header("🏢 Manajemen Grup")
    
    # Tambah Grup Baru
    with st.expander("➕ Buat Grup Baru"):
        new_group_name = st.text_input("Nama Grup:")
        g_token = st.text_input("Bot Token (Opsional):", help="Kosongkan jika ingin bot default")
        g_chatid = st.text_input("Chat ID (Opsional):")
        if st.button("Buat Grup"):
            if new_group_name and new_group_name not in db["groups"]:
                db["groups"][new_group_name] = {
                    "token": g_token if g_token else db["groups"]["Default"]["token"],
                    "chat_id": g_chatid if g_chatid else db["groups"]["Default"]["chat_id"],
                    "members": {}
                }
                st.success(f"Grup {new_group_name} dibuat!")
                st.rerun()

    st.divider()
    
    # Tambah Akun ke Grup
    st.header("👤 Tambah Akun")
    target_group = st.selectbox("Pilih Grup Tujuan:", list(db["groups"].keys()))
    new_id = st.text_input("User ID Roblox:", placeholder="Contoh: 3410934690")
    
    if st.button("Simpan ke Grup"):
        if new_id.isdigit():
            uid = int(new_id)
            if uid not in db["groups"][target_group]["members"]:
                name = get_username(uid)
                db["groups"][target_group]["members"][uid] = {"name": name, "last_status": -1}
                if new_id not in db["history"]:
                    db["history"].append(new_id)
                st.success(f"{name} masuk ke {target_group}")
                st.rerun()

    if st.button("🔴 Hapus Semua Grup"):
        db["groups"] = {"Default": db["groups"]["Default"]}
        db["groups"]["Default"]["members"] = {}
        st.rerun()

# --- HALAMAN UTAMA: TAMPILAN GRID ---
for g_name, g_data in db["groups"].items():
    if not g_data["members"]:
        continue
        
    st.subheader(f"📍 Group: {g_name}")
    uids = list(g_data["members"].keys())
    
    try:
        # Ambil data presence dari Roblox
        res = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}).json()
        presences = {p['userId']: p['userPresenceType'] for p in res.get('userPresences', [])}
        
        # Tampilan 1 baris = 4 kolom
        cols = st.columns(4)
        for idx, uid in enumerate(uids):
            current_status = presences.get(uid, 0)
            old_status = g_data["members"][uid]["last_status"]
            name = g_data["members"][uid]["name"]
            
            # Notifikasi Keluar (per grup)
            if old_status == 2 and current_status != 2:
                send_telegram(g_data["token"], g_data["chat_id"], f"🔴 [{g_name}] {name} ({uid}) KELUAR Game")
            
            db["groups"][g_name]["members"][uid]["last_status"] = current_status
            
            # Tampilan di Grid
            with cols[idx % 4]:
                color = "🟢" if current_status == 2 else "🔴"
                with st.container(border=True):
                    st.markdown(f"**{color} {name}**")
                    st.caption(f"ID: {uid}")
                    if st.button("Hapus", key=f"del_{g_name}_{uid}"):
                        del db["groups"][g_name]["members"][uid]
                        st.rerun()
        st.divider()
    except:
        st.error(f"Gagal memuat data grup {g_name}")

# Auto Refresh 30 detik
time.sleep(30)
st.rerun()
