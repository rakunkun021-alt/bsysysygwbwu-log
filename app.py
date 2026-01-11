import streamlit as st
import requests
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Roblox Grid Monitor", layout="wide")

# CSS AGAR TAMPILAN KOTAK KECIL 4 KE SAMPING DI HP
st.markdown("""
    <style>
    /* Memaksa kolom berjejer ke samping tanpa turun kebawah */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 4px !important;
        justify-content: flex-start !important;
    }
    /* Mengatur lebar kotak agar pas 4 di layar HP */
    [data-testid="column"] {
        flex: 1 1 22% !important; /* Pas 4 kolom (22% x 4 = 88% + gap) */
        min-width: 70px !important;
        max-width: 24% !important;
        padding: 0px !important;
    }
    /* Styling kotak mirip katalog */
    .stContainer {
        border: 1px solid #333;
        border-radius: 5px;
        padding: 5px;
        background-color: #0e1117;
        text-align: center;
    }
    button[kind="secondary"] {
        padding: 0px 5px !important;
        height: 25px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def send_telegram(token, chat_id, message):
    if not token or not chat_id: return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=5)
    except: pass

# --- DATABASE ---
@st.cache_resource
def get_db():
    return {
        "groups": {"Utama": {"token": "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k", "chat_id": "8170247984", "members": {}}},
        "history_id": [],
        "history_token": ["8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k"],
        "history_chatid": ["8170247984"]
    }

db = get_db()

# --- SIDEBAR: KONFIGURASI ---
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    
    # BAGIAN 1: BUAT GRUP DENGAN RIWAYAT BOT
    with st.expander("➕ Buat/Edit Grup"):
        gn = st.text_input("Nama Grup:")
        # Input Token dengan Riwayat
        tk = st.selectbox("Token Bot (Ketik/Pilih):", options=list(dict.fromkeys([""] + db["history_token"])), index=0)
        # Input Chat ID dengan Riwayat
        ci = st.selectbox("Chat ID (Ketik/Pilih):", options=list(dict.fromkeys([""] + db["history_chatid"])), index=0)
        
        # Jika user mengetik manual (tidak ada di list), kita tampung lewat text_input cadangan
        custom_tk = st.text_input("Atau ketik Token baru:")
        custom_ci = st.text_input("Atau ketik Chat ID baru:")
        
        final_tk = custom_tk if custom_tk else tk
        final_ci = custom_ci if custom_ci else ci

        if st.button("Simpan Grup"):
            if gn and final_tk and final_ci:
                db["groups"][gn] = {"token": final_tk, "chat_id": final_ci, "members": {}}
                if final_tk not in db["history_token"]: db["history_token"].append(final_tk)
                if final_ci not in db["history_chatid"]: db["history_chatid"].append(final_ci)
                st.rerun()

    st.divider()

    # BAGIAN 2: TAMBAH ID DENGAN RIWAYAT
    st.subheader("👤 Tambah Akun")
    tgt = st.selectbox("Ke Grup:", list(db["groups"].keys()))
    
    # Riwayat ID: Bisa pilih atau ketik baru
    raw_id = st.selectbox("User ID (Pilih/Ketik di bawah):", options=["-- Baru --"] + db["history_id"])
    new_id_input = st.text_input("Ketik ID baru disini:", value="" if raw_id == "-- Baru --" else raw_id)

    if st.button("Tambahkan Ke List"):
        if new_id_input.isdigit():
            uid = int(new_id_input)
            try:
                res = requests.get(f"https://users.roblox.com/v1/users/{uid}").json()
                name = res.get('name', f"User-{uid}")
                db["groups"][tgt]["members"][uid] = {"name": name, "last_status": -1}
                if new_id_input not in db["history_id"]: db["history_id"].append(new_id_input)
                st.rerun()
            except: st.error("Gagal koneksi")

# --- TAMPILAN UTAMA ---
st.title("🎮 Roblox Group Monitor")

for g_name, g_data in db["groups"].items():
    if g_data["members"]:
        st.subheader(f"📍 {g_name}")
        uids = list(g_data["members"].keys())
        
        try:
            res = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}).json()
            pres = {p['userId']: p['userPresenceType'] for p in res.get('userPresences', [])}
            
            # MENGGUNAKAN COLUMNS(4) UNTUK GRID
            cols = st.columns(4)
            for i, uid in enumerate(uids):
                curr = pres.get(uid, 0)
                old = g_data["members"][uid]["last_status"]
                name = g_data["members"][uid]["name"]
                
                if old == 2 and curr != 2:
                    send_telegram(g_data["token"], g_data["chat_id"], f"🔴 {name} Keluar")
                
                db["groups"][g_name]["members"][uid]["last_status"] = curr
                
                with cols[i % 4]: # Ini yang membuat otomatis pindah baris setiap 4 item
                    with st.container(border=True):
                        st.write("🟢" if curr==2 else "🔴")
                        st.caption(name[:7]) # Nama singkat agar pas di kotak kecil
                        if st.button("🗑️", key=f"del_{g_name}_{uid}"):
                            del db["groups"][g_name]["members"][uid]
