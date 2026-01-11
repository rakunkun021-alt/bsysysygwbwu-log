import streamlit as st
import requests
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Roblox Monitor Pro", layout="wide")

# CSS Tambahan agar di HP tetap kotak-kotak (Grid)
st.markdown("""
    <style>
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
    }
    [data-testid="column"] {
        min-width: 150px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def send_telegram(token, chat_id, message):
    if not token or not chat_id: return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=5)
    except: pass

# --- DATABASE PERMANEN ---
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
        "last_saved": {} # Untuk fitur Riwayat Cerdas
    }

db = get_global_data()

with st.sidebar:
    st.header("⚙️ Menu Admin")
    
    # Tombol Pulihkan Riwayat
    if db["last_saved"] and st.button("🔄 Pulihkan Data Terakhir"):
        db["groups"] = db["last_saved"].copy()
        st.rerun()

    with st.expander("➕ Tambah Grup & Bot Baru"):
        n_g = st.text_input("Nama Grup:")
        n_t = st.text_input("Token Bot Telegram:")
        n_c = st.text_input("Chat ID Telegram:")
        if st.button("Buat Grup"):
            if n_g:
                db["groups"][n_g] = {
                    "token": n_t if n_t else db["groups"]["Utama"]["token"],
                    "chat_id": n_c if n_c else db["groups"]["Utama"]["chat_id"],
                    "members": {}
                }
                db["last_saved"] = db["groups"].copy() # Simpan riwayat
                st.rerun()

    st.divider()
    st.subheader("👤 Tambah Akun")
    target = st.selectbox("Pilih Grup:", list(db["groups"].keys()))
    new_id = st.text_input("User ID Roblox:")
    
    if st.button("Simpan Ke Pantauan"):
        if new_id.isdigit():
            uid = int(new_id)
            try:
                res = requests.get(f"https://users.roblox.com/v1/users/{uid}").json()
                name = res.get('name', f"User-{uid}")
                db["groups"][target]["members"][uid] = {"name": name, "last_status": -1}
                db["last_saved"] = db["groups"].copy() # Simpan riwayat
                st.rerun()
            except: st.error("ID tidak valid")

    if st.button("🔴 Reset Total"):
        db["groups"] = {"Utama": {"token": "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k", "chat_id": "8170247984", "members": {}}}
        db["last_saved"] = {}
        st.rerun()

# --- TAMPILAN UTAMA ---
st.title("📱 Roblox Group Monitor")

for g_name, g_data in db["groups"].items():
    if g_data["members"]:
        st.subheader(f"📍 Grup: {g_name}")
        uids = list(g_data["members"].keys())
        
        try:
            res = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}).json()
            pres = {p['userId']: p['userPresenceType'] for p in res.get('userPresences', [])}
            
            # Loop Grid (4 ID per baris)
            for i in range(0, len(uids), 4):
                cols = st.columns(4)
                for j, uid in enumerate(uids[i:i+4]):
                    curr = pres.get(uid, 0)
                    old = g_data["members"][uid]["last_status"]
                    name = g_data["members"][uid]["name"]
                    
                    if old == 2 and curr != 2:
                        send_telegram(g_data["token"], g_data["chat_id"], f"🔴 [{g_name}] {name} Keluar")
                    
                    db["groups"][g_name]["members"][uid]["last_status"] = curr
                    
                    with cols[j]:
                        with st.container(border=True):
                            st.write(f"{'🟢' if curr==2 else '🔴'} **{name}**")
                            st.caption(f"ID: {uid}")
                            if st.button("Hapus", key=f"btn_{g_name}_{uid}"):
                                del db["groups"][g_name]["members"][uid]
                                db["last_saved"] = db["groups"].copy()
                                st.rerun()
        except: st.error("Koneksi API Roblox Terganggu")

time.sleep(30)
st.rerun()
