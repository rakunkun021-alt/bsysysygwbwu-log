import streamlit as st
import requests
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Roblox Grid Monitor", layout="wide")

# CSS AGAR TAMPILAN KECIL 4 KE SAMPING DI HP
st.markdown("""
    <style>
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 4px !important;
    }
    [data-testid="column"] {
        flex: 1 1 23% !important;
        min-width: 75px !important;
        max-width: 24% !important;
        padding: 0px !important;
    }
    .stContainer {
        border: 1px solid #333;
        border-radius: 5px;
        padding: 5px;
        text-align: center;
        background-color: #0e1117;
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
        "h_id": [], 
        "h_tk": ["8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k"], 
        "h_ci": ["8170247984"]
    }

db = get_db()

# --- SIDEBAR: KONFIGURASI ---
with st.sidebar:
    st.header("⚙️ Menu Admin")
    
    # 1. RIWAYAT TOKEN & CHAT ID
    with st.expander("➕ Grup & Bot"):
        gn = st.text_input("Nama Grup:")
        tk_sel = st.selectbox("Riwayat Token (Klik ^):", options=list(dict.fromkeys(db["h_tk"])))
        tk_new = st.text_input("Atau ketik Token baru:")
        ci_sel = st.selectbox("Riwayat Chat ID (Klik ^):", options=list(dict.fromkeys(db["h_ci"])))
        ci_new = st.text_input("Atau ketik Chat ID baru:")
        
        f_tk = tk_new if tk_new else tk_sel
        f_ci = ci_new if ci_new else ci_sel

        if st.button("Simpan Grup"):
            if gn:
                db["groups"][gn] = {"token": f_tk, "chat_id": f_ci, "members": {}}
                if f_tk and f_tk not in db["h_tk"]: 
                    db["h_tk"].append(f_tk)
                if f_ci and f_ci not in db["h_ci"]: 
                    db["h_ci"].append(f_ci)
                st.success(f"Grup {gn} Aktif")
                st.rerun()

    st.divider()

    # 2. RIWAYAT USER ID
    st.subheader("👤 Tambah Akun")
    tgt = st.selectbox("Pilih Grup Tujuan:", list(db["groups"].keys()))
    h_sel = st.selectbox("Riwayat User ID (Klik ^):", options=["-- Baru --"] + db["h_id"])
    u_input = st.text_input("Ketik User ID Roblox:", value="" if h_sel == "-- Baru --" else h_sel)

    if st.button("Tambahkan ke List"):
        if u_input.isdigit():
            uid = int(u_input)
            try:
                res = requests.get(f"https://users.roblox.com/v1/users/{uid}").json()
                name = res.get('name', f"User-{uid}")
                db["groups"][tgt]["members"][uid] = {"name": name, "last_status": -1}
                if u_input not in db["h_id"]: 
                    db["h_id"].append(u_input)
                st.success("Berhasil!")
                st.rerun()
            except: 
                st.error("ID tidak valid")

# --- TAMPILAN UTAMA ---
st.title("🎮 Monitoring")

for g_name, g_data in db["groups"].items():
    if g_data["members"]:
        st.subheader(f"📍 Grup: {g_name}")
        uids = list(g_data["members"].keys())
        
        try:
            res_call = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids})
            res = res_call.json()
            pres = {p['userId']: p['userPresenceType'] for p in res.get('userPresences', [])}
            
            # GRID 4 KOLOM
            cols = st.columns(4)
            for i, uid in enumerate(uids):
                curr = pres.get(uid, 0)
                old = g_data["members"][uid]["last_status"]
                name = g_data["members"][uid]["name"]
                
                # Cek Notif Keluar
                if old == 2 and curr != 2:
                    send_telegram(g_data["token"], g_data["chat_id"], f"🔴 {name} Keluar Game")
                
                db["groups"][g_name]["members"][uid]["last_status"] = curr
                
                with cols[i % 4]:
                    with st.container(border=True):
                        st.write("🟢" if curr == 2 else "🔴")
                        st.caption(name[:8])
                        if st.button("🗑️", key=f"del_{g_name}_{uid}"):
                            del db["groups"][g_name]["members"][uid]
                            st.rerun()
        except:
            st.write("Syncing data...")

time.sleep(30)
st.rerun()
