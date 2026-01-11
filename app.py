import streamlit as st
import requests
import time

# --- FUNGSI KIRIM TELEGRAM ---
def send_telegram(token, chat_id, message):
    if not token or not chat_id: return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=5)
    except: pass

# --- BARIS INI YANG MEMBUAT TAMPILAN JADI 4 KOLOM ---
st.set_page_config(
    page_title="Roblox Multi-Group", 
    page_icon="🎮", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

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
        }
    }

db = get_global_data()

# --- SIDEBAR: KONFIGURASI GRUP & BOT ---
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    
    # Fitur Tambah Grup/Bot
    with st.expander("➕ Tambah Grup / Bot Baru"):
        new_g_name = st.text_input("Nama Grup Baru:")
        g_token = st.text_input("Token Bot (Opsional):")
        g_chatid = st.text_input("Chat ID (Opsional):")
        if st.button("Buat Grup"):
            if new_g_name and new_g_name not in db["groups"]:
                db["groups"][new_g_name] = {
                    "token": g_token if g_token else db["groups"]["Utama"]["token"],
                    "chat_id": g_chatid if g_chatid else db["groups"]["Utama"]["chat_id"],
                    "members": {}
                }
                st.rerun()

    st.divider()
    
    # Tambah Akun
    st.subheader("👤 Tambah Akun")
    target_group = st.selectbox("Pilih Grup:", list(db["groups"].keys()))
    new_id = st.text_input("User ID Roblox:")
    
    if st.button("Simpan ID"):
        if new_id.isdigit():
            uid = int(new_id)
            if uid not in db["groups"][target_group]["members"]:
                res = requests.get(f"https://users.roblox.com/v1/users/{uid}").json()
                name = res.get('name', f"User-{uid}")
                db["groups"][target_group]["members"][uid] = {"name": name, "last_status": -1}
                st.success(f"Berhasil!")
                st.rerun()

# --- HALAMAN UTAMA: TAMPILAN GRID 4 KOLOM ---
for g_name, g_data in db["groups"].items():
    if g_data["members"]:
        st.subheader(f"📍 Grup: {g_name}")
        uids = list(g_data["members"].keys())
        
        try:
            res = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}).json()
            pres = {p['userId']: p['userPresenceType'] for p in res.get('userPresences', [])}
            
            # Membuat Baris dengan 4 Kolom
            for i in range(0, len(uids), 4):
                cols = st.columns(4)
                for j, uid in enumerate(uids[i:i+4]):
                    curr = pres.get(uid, 0)
                    old = g_data["members"][uid]["last_status"]
                    name = g_data["members"][uid]["name"]
                    
                    if old == 2 and curr != 2:
                        send_telegram(g_data["token"], g_data["chat_id"], f"🔴 [{g_name}] {name} Keluar")
                    
                    db["groups"][g_name]["members"][uid]["last_status"] = curr
                    
                    with cols[j]:
                        with st.container(border=True):
                            color = "🟢" if curr == 2 else "🔴"
                            st.markdown(f"**{color} {name}**")
                            st.caption(f"ID: {uid}")
                            if st.button("Hapus", key=f"del_{g_name}_{uid}"):
                                del db["groups"][g_name]["members"][uid]
                                st.rerun()
        except:
            st.error(f"Error pada grup {g_name}")

time.sleep(30)
st.rerun()
