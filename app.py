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

st.set_page_config(page_title="Roblox Monitor Pro", page_icon="🎮", layout="wide")
st.title("📱 Roblox Permanent Log")

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

# --- SIDEBAR: KONFIGURASI & LAST EVENTS ---
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    
    new_id = st.text_input("Tambah User ID:", placeholder="Masukkan angka...")
    if st.button("Simpan ID"):
        if new_id.isdigit():
            uid = int(new_id)
            if uid not in persistent_data["user_list"]:
                name = get_username(uid)
                persistent_data["user_list"][uid] = {"name": name, "last_status": -1}
                if new_id not in persistent_data["history"]:
                    persistent_data["history"].append(new_id)
                st.success(f"Menambah {name}")
                st.rerun()

    if persistent_data["history"]:
        st.divider()
        st.subheader("📜 Riwayat ID")
        sel = st.selectbox("Pilih ID lama:", ["-- Pilih --"] + persistent_data["history"])
        if sel != "-- Pilih --" and st.button("Pantau Kembali"):
            uid = int(sel)
            if uid not in persistent_data["user_list"]:
                name = get_username(uid)
                persistent_data["user_list"][uid] = {"name": name, "last_status": -1}
                st.rerun()

    # --- BAGIAN LAST EVENTS ---
    st.divider()
    st.subheader("🕒 Last Events (Keluar)")
    if persistent_data["event_logs"]:
        # Tampilkan 10 kejadian terakhir
        for log in reversed(persistent_data["event_logs"][-10:]):
            st.caption(log)
        if st.button("🗑️ Bersihkan Log"):
            persistent_data["event_logs"] = []
            st.rerun()
    else:
        st.write("Belum ada aktivitas keluar.")

# --- HALAMAN UTAMA: MONITORING ---
if persistent_data["user_list"]:
    uids = list(persistent_data["user_list"].keys())
    try:
        res_call = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids})
        res = res_call.json()
        
        st.subheader("Daftar Pantauan")
        for user in res.get('userPresences', []):
            uid = user['userId']
            name = persistent_data["user_list"][uid]["name"]
            curr_status = user['userPresenceType'] 
            old_status = persistent_data["user_list"][uid]["last_status"]

            # Logika Notif Keluar & Simpan ke Last Event
            if old_status == 2 and curr_status != 2:
                waktu = get_wib_time()
                msg = f"🔴 {name} ({uid}) KELUAR Game jam {waktu}"
                send_telegram(msg)
                persistent_data["event_logs"].append(f"🔴 {waktu} - {name} Keluar")
            
            persistent_data["user_list"][uid]["last_status"] = curr_status

            col1, col2 = st.columns([5, 1])
            with col1:
                color = "🟢" if curr_status == 2 else "🔴"
                st.info(f"{color} **{name}** ({uid}) | {'IN-GAME' if curr_status == 2 else 'OFFLINE'}")
            with col2:
                if st.button("Hapus", key=f"del_{uid}"):
                    del persistent_data["user_list"][uid]
                    st.rerun()
    except:
        st.error("Gagal update data.")
else:
    st.info("Gunakan Sidebar untuk menambah akun.")

# Tambahan: Pesan agar Cron-job mengenali halaman
st.write("---")
st.caption("Status: Active Monitoring Background")

time.sleep(30)
st.rerun()
