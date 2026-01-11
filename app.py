import streamlit as st
import requests
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Roblox Grid Monitor", layout="wide")

# CSS KHUSUS AGAR TAMPILAN SEPERTI ITEMKU (Grid 4 Kolom di HP)
st.markdown("""
    <style>
    /* Mengatur jarak antar kotak agar pas 4 ke samping */
    [data-testid="column"] {
        width: 23% !important;
        flex: 1 1 23% !important;
        min-width: 80px !important;
        padding: 5px !important;
    }
    /* Kotak ID agar rapi dan kecil */
    .stContainer {
        border: 1px solid #444;
        border-radius: 8px;
        padding: 8px;
        text-align: center;
        background-color: #1e1e1e;
    }
    /* Memaksa elemen berjejer ke samping */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 5px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def send_telegram(token, chat_id, message):
    if not token or not chat_id: return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=5)
    except: pass

# --- DATABASE RIWAYAT OTOMATIS ---
@st.cache_resource
def get_global_data():
    return {
        "groups": {
            "Utama": {
                "token": "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k",
                "chat_id": "8170247984",
                "members": {} 
            }
        },
        "history_ids": [],
        "history_bots": [] # Simpan riwayat Token & ChatID
    }

db = get_global_data()

# --- SIDEBAR: KONFIGURASI ---
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    
    # Riwayat Bot & Chat ID
    with st.expander("🤖 Riwayat Bot Telegram"):
        if db["history_bots"]:
            for i, h in enumerate(db["history_bots"]):
                if st.button(f"Gunakan Bot {i+1}", key=f"hbot_{i}"):
                    # Logika untuk set token/chatid grup
                    st.info("Bot terpilih. Masukkan nama grup di bawah.")
        else:
            st.write("Belum ada riwayat bot.")

    st.divider()
    
    # Tambah Grup Baru
    with st.expander("➕ Tambah Grup/Bot"):
        n_g = st.text_input("Nama Grup:")
        n_t = st.text_input("Token Bot:")
        n_c = st.text_input("Chat ID:")
        if st.button("Simpan Grup"):
            if n_g:
                db["groups"][n_g] = {
                    "token": n_t if n_t else db["groups"]["Utama"]["token"],
                    "chat_id": n_c if n_c else db["groups"]["Utama"]["chat_id"],
                    "members": {}
                }
                # Simpan ke riwayat bot jika baru
                bot_info = {"t": n_t, "c": n_c}
                if bot_info not in db["history_bots"]: db["history_bots"].append(bot_info)
                st.rerun()

    st.divider()

    # Tambah ID dengan Riwayat
    st.subheader("👤 Tambah ID")
    target = st.selectbox("Grup:", list(db["groups"].keys()))
    
    # Input ID dengan pilihan riwayat
    u_id_input = st.selectbox("Riwayat ID:", ["-- Input Baru --"] + db["history_ids"])
    if u_id_input == "-- Input Baru --":
        new_id = st.text_input("Ketik ID Baru:")
    else:
        new_id = u_id_input

    if st.button("Tambahkan"):
        if new_id.isdigit():
            uid = int(new_id)
            try:
                res = requests.get(f"https://users.roblox.com/v1/users/{uid}").json()
                name = res.get('name', f"User-{uid}")
                db["groups"][target]["members"][uid] = {"name": name, "last_status": -1}
                if new_id not in db["history_ids"]: db["history_ids"].append(new_id)
                st.rerun()
            except: st.error("ID Gagal")

# --- TAMPILAN UTAMA (SISTEM GRID SEPERTI ITEMKU) ---
st.title("📱 Roblox Group Monitor")

for g_name, g_data in db["groups"].items():
    if g_data["members"]:
        st.subheader(f"📍 {g_name}")
        uids = list(g_data["members"].keys())
        
        try:
            res = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}).json()
            pres = {p['userId']: p['userPresenceType'] for p in res.get('userPresences', [])}
            
            # Membuat Grid Otomatis (4 kolom)
            cols = st.columns(4)
            for idx, uid in enumerate(uids):
                curr = pres.get(uid, 0)
                old = g_data["members"][uid]["last_status"]
                name = g_data["members"][uid]["name"]
                
                # Notif Keluar
                if old == 2 and curr != 2:
                    send_telegram(g_data["token"], g_data["chat_id"], f"🔴 [{g_name}] {name} Keluar")
                
                db["groups"][g_name]["members"][uid]["last_status"] = curr
                
                # Masukkan ke kolom (0, 1, 2, 3 lalu balik ke 0)
                with cols[idx % 4]:
                    with st.container(border=True):
                        st.write(f"{'🟢' if curr==2 else '🔴'}")
                        st.markdown(f"**{name[:8]}**") # Potong nama agar tidak kepanjangan
                        if st.button("🗑️", key=f"h_{g_name}_{uid}"):
                            del db["groups"][g_name]["members"][uid]
                            st.rerun()
        except: st.error("API Limit")

# Auto Refresh
time.sleep(30)
st.rerun()
