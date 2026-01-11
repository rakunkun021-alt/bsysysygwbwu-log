import streamlit as st
import requests
import time
import json

# --- CONFIG & CSS ---
st.set_page_config(page_title="Roblox Monitor", layout="wide")

# CSS Kuat untuk Grid 4 Kolom & Nama Utuh
st.markdown("""
    <style>
    div[data-testid="stColumn"] {
        flex: 1 1 23% !important;
        min-width: 80px !important;
        padding: 2px !important;
    }
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
    }
    .stContainer {
        border: 1px solid #444;
        border-radius: 8px;
        background-color: #1a1c24;
        padding: 5px;
        text-align: center;
        min-height: 100px;
    }
    small { font-size: 10px; color: #aaa; }
    </style>
    """, unsafe_allow_html=True)

def send_telegram(token, chat_id, message):
    if not token or not chat_id: return
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                      json={"chat_id": chat_id, "text": message}, timeout=5)
    except: pass

# --- SISTEM PENYIMPANAN ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "groups": {"Utama": {"token": "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k", "chat_id": "8170247984", "members": {}}},
        "h_id": [], "h_tk": ["8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k"], "h_ci": ["8170247984"]
    }

db = st.session_state.db

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    
    # Fitur Anti Hilang (Backup/Restore)
    with st.expander("💾 Backup & Restore (Anti Hilang)"):
        data_str = json.dumps(db)
        st.text_area("Salin & Simpan Kode Ini ke Catatan HP:", value=data_str, height=100)
        restore = st.text_input("Tempel Kode Backup di sini untuk Restore:")
        if st.button("Restore Data"):
            try:
                st.session_state.db = json.loads(restore)
                st.rerun()
            except: st.error("Kode Salah")

    # Input Bot
    with st.expander("🤖 Bot & Grup"):
        gn = st.text_input("Nama Grup Baru:")
        tk = st.selectbox("Riwayat Token:", options=db["h_tk"])
        tk_new = st.text_input("Ketik Token Baru (Jika beda):")
        ci = st.selectbox("Riwayat Chat ID:", options=db["h_ci"])
        ci_new = st.text_input("Ketik Chat ID Baru (Jika beda):")
        
        if st.button("Simpan Grup"):
            final_tk = tk_new if tk_new else tk
            final_ci = ci_new if ci_new else ci
            db["groups"][gn] = {"token": final_tk, "chat_id": final_ci, "members": {}}
            if final_tk not in db["h_tk"]: db["h_tk"].append(final_tk)
            if final_ci not in db["h_ci"]: db["h_ci"].append(final_ci)
            st.rerun()

    st.divider()
    
    # Input ID
    st.subheader("👤 Tambah Akun")
    target = st.selectbox("Ke Grup:", list(db["groups"].keys()))
    h_sel = st.selectbox("Riwayat ID:", options=["-- Baru --"] + db["h_id"])
    u_input = st.text_input("Input ID Roblox:", value="" if h_sel == "-- Baru --" else h_sel)

    if st.button("Tambahkan"):
        if u_input.isdigit():
            try:
                res = requests.get(f"https://users.roblox.com/v1/users/{u_input}").json()
                name = res.get('name', f"User-{u_input}")
                db["groups"][target]["members"][u_input] = {"name": name, "last": -1}
                if u_input not in db["h_id"]: db["h_id"].append(u_input)
                st.rerun()
            except: st.error("Gagal")

# --- MAIN UI ---
st.title("🎮 Monitoring Center")

for g_name, g_data in db["groups"].items():
    if g_data["members"]:
        st.subheader(f"📍 {g_name}")
        uids = list(g_data["members"].keys())
        
        try:
            r = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}).json()
            pres = {str(p['userId']): p['userPresenceType'] for p in r.get('userPresences', [])}
            
            cols = st.columns(4)
            for i, uid in enumerate(uids):
                curr = pres.get(uid, 0)
                old = g_data["members"][uid]["last"]
                name = g_data["members"][uid]["name"]
                
                if old == 2 and curr != 2:
                    send_telegram(g_data["token"], g_data["chat_id"], f"🔴 {name} Keluar")
                
                db["groups"][g_name]["members"][uid]["last"] = curr
                
                with cols[i % 4]:
                    st.markdown(f"""
                    <div class="stContainer">
                        <h2 style='margin:0;'>{'🟢' if curr==2 else '🔴'}</h2>
                        <b style='font-size:12px;'>{name}</b><br>
                        <small>{uid}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_{g_name}_{uid}"):
                        del db["groups"][g_name]["members"][uid]
                        st.rerun()
        except: st.write("Wait...")

time.sleep(30)
st.rerun()
