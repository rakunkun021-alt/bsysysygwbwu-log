import streamlit as st
import requests
import time
from datetime import datetime
import pytz

# --- DATA TELEGRAM ---
TOKEN = "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k"
CHAT_ID = "8170247984"

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": message}, timeout=5)
    except:
        pass

# Setup Halaman - Sidebar otomatis terbuka
st.set_page_config(
    page_title="Roblox Monitor Pro", 
    page_icon="🎮", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SISTEM PENYIMPANAN PERMANEN ---
@st.cache_resource
def get_global_data():
    return {
        "user_list": {}, 
        "history": [],    
        "event_logs": []  
    }

persistent_data = get_global_data()

def get_wib_time():
    tz = pytz.timezone('Asia/Jakarta')
    return datetime.now(tz).strftime("%H:%M:%S")

def get_username(uid):
    try:
        res = requests.get(f"https://users.roblox.com/v1/users/{uid}").json()
        return res.get('name', f"User-{uid}")
    except:
        return f"User-{uid}"

# --- SIDEBAR (SISI KIRI): HANYA KONFIGURASI ---
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    st.write("Gunakan menu ini untuk mengelola akun.")
    
    new_id = st.text_input("Tambah User ID:", placeholder="Masukkan angka...")
    if st.button("Simpan ID Baru"):
        if new_id.isdigit():
            uid = int(new_id)
            if uid not in persistent_data["user_list"]:
                name = get_username(uid)
                persistent_data["user_list"][uid] = {"name": name, "last_status": -1}
                if new_id not in persistent_data["history"]:
                    persistent_data["history"].append(new_id)
                st.success(f"Berhasil: {name}")
                st.rerun()

    if persistent_data["history"]:
        st.divider()
        st.subheader("📜 Riwayat ID")
        sel = st.selectbox("Pilih dari riwayat:", ["-- Pilih --"] + persistent_data["history"])
        if sel != "-- Pilih --" and st.button("Pantau Lagi"):
            uid = int(sel)
            if uid not in persistent_data["user_list"]:
                name = get_username(uid)
                persistent_data["user_list"][uid] = {"name": name, "last_status": -1}
                st.rerun()

    st.divider()
    if st.button("🔴 Reset Semua Pantauan"):
        persistent_data["user_list"] = {}
        st.rerun()

# --- HALAMAN UTAMA (SISI KANAN & TENGAH): MONITORING & LAST EVENTS ---
# Kita bagi layar menjadi dua kolom
col_monitor, col_events = st.columns([2, 1])

with col_monitor:
    st.header("🎮 Live Monitoring")
    if persistent_data["user_list"]:
        uids = list(persistent_data["user_list"].keys())
        try:
            res_call = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids})
            res = res_call.json()
            
            for user in res.get('userPresences', []):
                uid = user['userId']
                name = persistent_data["user_list"][uid]["name"]
                curr_status = user['userPresenceType'] 
                old_status = persistent_data["user_list"][uid]["last_status"]

                # Logika Notif Keluar
                if old_status == 2 and curr_status != 2:
                    waktu = get_wib_time()
                    msg = f"🔴 {name} ({uid}) KELUAR pada {waktu}"
                    send_telegram(msg)
                    # Masukkan ke Log
                    persistent_data["event_logs"].append(f"🔴 **{waktu}** - {name}")
                
                persistent_data["user_list"][uid]["last_status"] = curr_status

                # Tampilan Baris Akun
                c1, c2 = st.columns([4, 1])
                with c1:
                    color = "🟢" if curr_status == 2 else "🔴"
                    st.info(f"{color} **{name}** ({uid})")
                with c2:
                    if st.button("Hapus", key=f"del_{uid}"):
                        del persistent_data["user_list"][uid]
                        st.rerun()
        except:
            st.error("Gagal mengambil data dari Roblox.")
    else:
        st.info("Belum ada akun. Tambahkan ID melalui sidebar di sisi kiri.")

with col_events:
    st.header("🕒 Last Events")
    st.write("Riwayat akun yang keluar:")
    if persistent_data["event_logs"]:
        # Menampilkan 20 kejadian terakhir
        for log in reversed(persistent_data["event_logs"][-20:]):
            st.markdown(log)
        
        if st.button("🗑️ Bersihkan Riwayat"):
            persistent_data["event_logs"] = []
            st.rerun()
    else:
        st.caption("Belum ada aktivitas yang tercatat.")

# Auto Refresh 30 detik
time.sleep(30)
st.rerun()
