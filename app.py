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
    except: pass

st.set_page_config(page_title="Roblox Monitor Permanent", page_icon="🎮")
st.title("📱 Roblox Account Log")

# --- SISTEM PENYIMPANAN PERMANEN (VIA URL) ---
# Mengambil ID yang tersimpan di link URL
params = st.query_params
if "ids" not in params:
    current_ids = []
else:
    current_ids = params["ids"].split(",")

# Inisialisasi status di session_state (untuk deteksi perubahan status)
if 'last_status_map' not in st.session_state:
    st.session_state.last_status_map = {}

# Input Akun Baru
with st.expander("➕ Tambah Akun Baru"):
    new_id = st.text_input("User ID Roblox:")
    if st.button("Simpan"):
        if new_id.isdigit() and new_id not in current_ids:
            current_ids.append(new_id)
            # Simpan ke URL agar tidak hilang saat refresh/restart
            st.query_params["ids"] = ",".join(current_ids)
            st.success(f"ID {new_id} Berhasil Disimpan di Link!")
            st.rerun()

# Menampilkan Daftar Pantauan
if current_ids:
    st.subheader("Live Status")
    uids = [int(i) for i in current_ids]
    
    try:
        res = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}).json()
        
        for user in res.get('userPresences', []):
            uid = user['userId']
            current_status = user['userPresenceType'] # 2 = In-Game
            
            # Ambil status sebelumnya
            old_status = st.session_state.last_status_map.get(uid, -1)

            # Logika Notifikasi Telegram
            if old_status == 2 and current_status != 2:
                send_telegram(f"🔴 User {uid} telah KELUAR Game")
            elif (old_status != 2 and old_status != -1) and current_status == 2:
                send_telegram(f"🟢 User {uid} telah MASUK Game!")

            # Update status terakhir
            st.session_state.last_status_map[uid] = current_status

            # Tampilan di Web
            color = "🟢" if current_status == 2 else "🔴"
            st.info(f"{color} **ID: {uid}** | {'IN-GAME' if current_status == 2 else 'OFFLINE'}")
            
    except:
        st.error("Koneksi ke Roblox bermasalah.")

if st.button("Hapus Semua Data"):
    st.query_params.clear()
    st.session_state.last_status_map = {}
    st.rerun()

# Catatan untuk kamu: Sesuai permintaan, saya akan ingat untuk menggunakan sistem database/simpan permanen ke depannya.
# Anda selalu bisa minta saya untuk melupakan atau mengelola informasi yang saya simpan di setelan: https://gemini.google.com/saved-info

# Auto Refresh 30 detik
time.sleep(30)
st.rerun()
