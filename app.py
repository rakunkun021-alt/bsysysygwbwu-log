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
        print(f"Error kirim Telegram: {e}")

st.set_page_config(page_title="Roblox Log Telegram", page_icon="🎮")
st.title("📱 Roblox Account Log")
st.caption("Notifikasi akan dikirim otomatis ke Telegram kamu.")

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
                # Set status awal ke -1 agar tidak langsung kirim notif saat baru ditambah
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
            current_status = user['userPresenceType'] # 2 = In-Game
            last_status = st.session_state.user_data[uid]['status']

            # --- LOGIKA NOTIFIKASI ---
            # Jika status berubah dari In-Game ke Keluar
            if last_status == 2 and current_status != 2:
                msg = f"🔴 NOTIF: {name} ({uid}) telah KELUAR dari server game."
                send_telegram(msg)
                st.toast(msg) # Muncul notif kecil di web
            
            # Jika status berubah dari Luar ke Masuk Server
            elif (last_status != 2 and last_status != -1) and current_status == 2:
                msg = f"🟢 NOTIF: {name} ({uid}) telah MASUK ke server game!"
                send_
