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

st.set_page_config(page_title="Roblox Monitor Non-Stop", page_icon="🎮")
st.title("📱 Roblox Account Log")

# --- SISTEM PENYIMPANAN AGAR TIDAK HILANG ---
@st.cache_resource
def get_global_data():
    return {"user_list": {}}

persistent_data = get_global_data()

def get_username(uid):
    try:
        res = requests.get(f"https://users.roblox.com/v1/users/{uid}").json()
        return res.get('name', f"User-{uid}")
    except:
        return f"User-{uid}"

with st.expander("➕ Tambah Akun Baru"):
    new_id = st.text_input("User ID Roblox:")
    if st.button("Simpan"):
        if new_id.isdigit():
            uid = int(new_id)
            if uid not in persistent_data["user_list"]:
                name = get_username(uid)
                persistent_data["user_list"][uid] = {"name": name, "last_status": -1}
                st.success(f"Berhasil menambah {name}")
                st.rerun()

if persistent_data["user_list"]:
    uids = list(persistent_data["user_list"].keys())
    
    try:
        res_call = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids})
        res = res_call.json()
        
        st.subheader("Daftar Pantauan")
        for user in res.get('userPresences', []):
            uid = user['userId']
            name = persistent_data["user_list"][uid]["name"]
            current_status = user['userPresenceType'] # 2 = In-Game
            old_status = persistent_data["user_list"][uid]["last_status"]

            # --- LOGIKA NOTIFIKASI (HANYA KELUAR) ---
            if old_status == 2 and current_status != 2:
                msg = f"🔴 {name} ({uid}) telah KELUAR dari server game."
                send_telegram(msg)
            
            # Update status di memori server
            persistent_data["user_list"][uid]["last_status"] = current_status

            # Tampilan Web
            color = "🟢" if current_status == 2 else "🔴"
            st.info(f"{color} **{name}** ({uid})\n\nStatus: {'IN-GAME' if current_status == 2 else 'OFFLINE'}")

    except Exception as e:
        st.error(f"Gagal update data: {e}")

if st.button("Hapus Semua Data"):
    persistent_data["user_list"] = {}
    st.rerun()

# Auto Refresh 30 detik
time.sleep(30)
st.rerun()
