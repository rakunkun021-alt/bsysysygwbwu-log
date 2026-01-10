import streamlit as st
import requests
import time

# --- DATA TELEGRAM KAMU ---
TOKEN = "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k"
CHAT_ID = "8170247984"

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        requests.post(url, json=payload)
    except Exception as e:
        pass

st.set_page_config(page_title="Roblox Log Telegram", page_icon="🎮")
st.title("📱 Roblox Account Log")

# Inisialisasi data akun
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

def get_username(user_id):
    try:
        res = requests.get(f"https://users.roblox.com/v1/users/{user_id}")
        return res.json().get('name', f"User-{user_id}")
    except:
        return f"User-{user_id}"

# Menu Input
with st.expander("➕ Tambah Akun Baru"):
    new_id = st.text_input("Masukkan User ID Roblox:")
    if st.button("Simpan Akun"):
        if new_id.isdigit():
            uid = int(new_id)
            if uid not in st.session_state.user_data:
                name = get_username(uid)
                st.session_state.user_data[uid] = {'name': name, 'status': -1}
                st.success(f"Berhasil menambah {name}")
                st.rerun()

# Proses Pengecekan
if st.session_state.user_data:
    user_ids = list(st.session_state.user_data.keys())
    url_presence = "https://presence.roblox.com/v1/presence/users"
    
    try:
        response = requests.post(url_presence, json={"userIds": user_ids})
        presences = response.json().get('userPresences', [])

        st.subheader("Daftar Pantauan")
        for user in presences:
            uid = user['userId']
            name = st.session_state.user_data[uid]['name']
            current_status = user['userPresenceType'] 
            last_status = st.session_state.user_data[uid]['status']

            # Logika Notifikasi
            if last_status == 2 and current_status != 2:
                msg = f"🔴 {name} ({uid}) KELUAR dari server game."
                send_telegram(msg)
            elif (last_status != 2 and last_status != -1) and current_status == 2:
                msg = f"🟢 {name} ({uid}) MASUK ke server game!"
                send_telegram(msg)

            st.session_state.user_data[uid]['status'] = current_status

            # Tampilan Web
            color = "🟢" if current_status == 2 else "🔴"
            st.info(f"{color} **{name}** ({uid})\n\nStatus: {'IN-GAME' if current_status == 2 else 'OFFLINE'}")

    except Exception as e:
        st.error("Gagal mengambil data.")

if st.button("Reset Semua"):
    st.session_state.user_data = {}
    st.rerun()

# Auto Refresh
time.sleep(30)
st.rerun()
