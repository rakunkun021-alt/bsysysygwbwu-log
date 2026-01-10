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

st.set_page_config(page_title="Roblox Monitor Sidebar", page_icon="🎮")
st.title("📱 Roblox Account Log")

# --- SISTEM PENYIMPANAN PERMANEN ---
@st.cache_resource
def get_global_data():
    return {
        "user_list": {}, # Daftar yang sedang dipantau
        "history": []    # Riwayat ID yang pernah dimasukkan
    }

persistent_data = get_global_data()

def get_username(uid):
    try:
        res = requests.get(f"https://users.roblox.com/v1/users/{uid}").json()
        return res.get('name', f"User-{uid}")
    except:
        return f"User-{uid}"

# --- SIDEBAR: TAMBAH & RIWAYAT ---
with st.sidebar:
    st.header("Konfigurasi")
    
    # Input ID Manual
    new_id = st.text_input("Masukkan User ID Roblox:", placeholder="Contoh: 3410934690")
    
    if st.button("Simpan Ke Pantauan"):
        if new_id.isdigit():
            uid = int(new_id)
            if uid not in persistent_data["user_list"]:
                name = get_username(uid)
                persistent_data["user_list"][uid] = {"name": name, "last_status": -1}
                # Tambah ke riwayat jika belum ada
                if new_id not in persistent_data["history"]:
                    persistent_data["history"].append(new_id)
                st.success(f"Memantau {name}")
                st.rerun()

    st.divider()
    
    # Fitur Riwayat ID
    if persistent_data["history"]:
        st.subheader("📜 Riwayat ID")
        selected_history = st.selectbox("Pilih dari riwayat:", ["-- Pilih ID --"] + persistent_data["history"])
        
        if selected_history != "-- Pilih ID --":
            if st.button("Pantau ID Ini"):
                uid = int(selected_history)
                if uid not in persistent_data["user_list"]:
                    name = get_username(uid)
                    persistent_data["user_list"][uid] = {"name": name, "last_status": -1}
                    st.success(f"Menambah {name} dari riwayat")
                    st.rerun()
        
        if st.button("🗑️ Hapus Riwayat"):
            persistent_data["history"] = []
            st.rerun()

    st.divider()
    if st.button("🔴 Reset Semua Pantauan"):
        persistent_data["user_list"] = {}
        st.rerun()

# --- HALAMAN UTAMA: MONITORING ---
if persistent_data["user_list"]:
    uids = list(persistent_data["user_list"].keys())
    
    try:
        res_call = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids})
        res = res_call.json()
        
        st.subheader("Live Status")
        for user in res.get('userPresences', []):
            uid = user['userId']
            name = persistent_data["user_list"][uid]["name"]
            current_status = user['userPresenceType'] 
            old_status = persistent_data["user_list"][uid]["last_status"]

            # Logika Notifikasi Keluar
            if old_status == 2 and current_status != 2:
                msg = f"🔴 {name} ({uid}) telah KELUAR dari server game."
                send_telegram(msg)
            
            persistent_data["user_list"][uid]["last_status"] = current_status

            # Tampilan
            col1, col2 = st.columns([4, 1])
            with col1:
                color = "🟢" if current_status == 2 else "🔴"
                st.info(f"{color} **{name}** ({uid})\n\nStatus: {'IN-GAME' if current_status == 2 else 'OFFLINE'}")
            
            with col2:
                if st.button("Hapus", key=f"del_{uid}"):
                    del persistent_data["user_list"][uid]
                    st.rerun()
    except:
        st.error("Gagal update data.")
else:
    st.write("Belum ada akun yang dipantau. Silakan tambah lewat Sidebar di kiri atas.")

# Auto Refresh 30 detik
time.sleep(30)
st.rerun()
