import streamlit as st
import requests

# Konfigurasi Tampilan
st.set_page_config(page_title="Roblox Log", page_icon="🔴")
st.title("📱 My Roblox Account Log")

# Penyimpanan ID Sementara
if 'user_ids' not in st.session_state:
    st.session_state.user_ids = []

# Input ID Baru via Web
with st.expander("➕ Tambah Akun Baru"):
    new_id = st.text_input("Masukkan User ID Roblox:")
    if st.button("Simpan Akun"):
        if new_id.isdigit():
            st.session_state.user_ids.append(int(new_id))
            st.success(f"ID {new_id} ditambahkan!")
        else:
            st.error("ID harus berupa angka!")

# Tombol Reset
if st.button("Reset Semua Daftar"):
    st.session_state.user_ids = []
    st.rerun()

# Cek Status ke API Roblox
if st.session_state.user_ids:
    st.subheader("Live Status")
    url = "https://presence.roblox.com/v1/presence/users"
    try:
        response = requests.post(url, json={"userIds": st.session_state.user_ids})
        data = response.json()['userPresences']

        for user in data:
            # Penentuan Indikator
            is_ingame = user['userPresenceType'] == 2
            icon = "🟢" if is_ingame else "🔴"
            status_txt = "IN-SERVER" if is_ingame else "OUTSIDE/OFFLINE"
            location = user.get('lastLocation', 'Unknown') if is_ingame else "-"

            # Tampilan Ringan per Akun
            st.info(f"{icon} **ID: {user['userId']}**\n\nStatus: {status_txt} | Lokasi: {location}")
            
    except Exception as e:
        st.error("Gagal mengambil data dari Roblox.")
else:
    st.write("Daftar akun kosong. Silakan tambah ID di atas.")

# Refresh otomatis setiap 30 detik
st.empty()
import time
time.sleep(30)
st.rerun()