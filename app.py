import streamlit as st
import requests
import time

# --- DATA TELEGRAM ---
TOKEN = "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k"
CHAT_ID = "8170247984"

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": message}, timeout=5)
    except:
        pass

st.set_page_config(page_title="Roblox Monitor 24/7", page_icon="🎮")
st.title("📱 Roblox Permanent Log")

# --- SISTEM PENYIMPANAN STABIL ---
# Menggunakan cache_resource agar data menempel di server Streamlit
@st.cache_resource
def get_database():
    return {"users": {}}

db = get_database()

def get_username(uid):
    try:
        res = requests.get(f"https://users.roblox.com/v1/users/{uid}").json()
        return res.get('name', f"User-{uid}")
    except:
        return f"User-{uid}"

# --- MENU TAMBAH ---
with st.sidebar:
    st.header("Settings")
    new_id = st.text_input("Tambah User ID:")
    if st.button("Simpan ID"):
        if new_id.isdigit():
            uid = int(new_id)
            if uid not in db["users"]:
                name = get_username(uid)
                db["users"][uid] = {"name": name, "status": -1}
                st.success(f"Monitoring {name}")
                st.rerun()
    
    if st.button("🔴 Hapus Semua Data"):
        db["users"] = {}
        st.rerun()

# --- PROSES MONITORING ---
if db["users"]:
    uids = list(db["users"].keys())
    try:
        res = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}).json()
        
        for user in res.get('userPresences', []):
            uid = user['userId']
            name = db["users"][uid]["name"]
            curr_status = user['userPresenceType'] # 2 = In-Game
            old_status = db["users"][uid]["status"]

            # Notif Hanya Keluar
            if old_status == 2 and curr_status != 2:
                send_telegram(f"🔴 {name} ({uid}) KELUAR Game")
            
            db["users"][uid]["status"] = curr_status

            # Tampilan List
            col1, col2 = st.columns([3, 1])
            with col1:
                color = "🟢" if curr_status == 2 else "🔴"
                st.info(f"{color} **{name}** ({uid})")
            with col2:
                if st.button("Hapus", key=f"del_{uid}"):
                    del db["users"][uid]
                    st.rerun()
    except:
        st.error("API Error")

# Trik agar aplikasi tetap aktif saat dibuka
st.caption("Aplikasi ini akan terus memantau selama tab ini atau Cron-job aktif.")
time.sleep(30)
st.rerun()
