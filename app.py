import streamlit as st
import requests
import time
import json

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Roblox Monitor Pro", layout="wide")

# CSS UNTUK PAKSA 4 KOLOM DI HP & RASIO 16:10
st.markdown("""
<style>
    /* Memaksa layout tetap menyamping (4 kolom) bahkan di layar HP */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        align-items: flex-start !important;
        justify-content: flex-start !important;
        gap: 6px !important;
    }

    /* Kunci lebar kolom tepat 25% minus gap agar pas 4 per baris */
    [data-testid="column"] {
        width: calc(25% - 6px) !important;
        flex: 0 0 calc(25% - 6px) !important;
        min-width: calc(25% - 6px) !important;
        margin-bottom: 5px !important;
    }

    /* Box Rasio 16:10 */
    .card-roblox {
        border: 1px solid #444;
        border-radius: 6px;
        background-color: #1a1c24;
        padding: 8px 4px;
        aspect-ratio: 16 / 10;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        width: 100%;
    }

    .user-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
        width: 100%;
    }

    .status-dot { 
        height: 8px; 
        width: 8px; 
        border-radius: 50%; 
        flex-shrink: 0;
    }
    .online { background-color: #2ecc71; box-shadow: 0 0 5px #2ecc71; }
    .offline { background-color: #e74c3c; }

    .username-text { 
        font-size: 10px; 
        font-weight: bold; 
        color: white;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .id-text { font-size: 8px; color: #888; }

    /* Tombol Hapus Kecil */
    .stButton > button {
        width: 100% !important;
        height: 22px !important;
        font-size: 8px !important;
        padding: 0px !important;
        margin-top: 3px !important;
    }
</style>
""", unsafe_allow_html=True)

def send_telegram(token, chat_id, message):
    if not token or not chat_id: return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=5)
    except: pass

# --- DATABASE SESSION ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "groups": {
            "Utama": {
                "token": "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k",
                "chat_id": "8170247984",
                "members": {}
            }
        },
        "h_id": []
    }

db = st.session_state.db

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Admin")
    with st.expander("💾 Backup & Restore"):
        st.code(json.dumps(db))
        res_code = st.text_area("Restore:")
        if st.button("Restore Now"):
            try:
                st.session_state.db = json.loads(res_code)
                st.rerun()
            except: st.error("Gagal")
    
    st.divider()
    target = st.selectbox("Grup:", list(db["groups"].keys()))
    u_in = st.text_input("ID Roblox:")
    if st.button("Tambah"):
        if u_in.isdigit():
            try:
                res = requests.get(f"https://users.roblox.com/v1/users/{u_in}").json()
                name = res.get('name', f"User-{u_in}")
                db["groups"][target]["members"][u_in] = {"name": name, "last": -1}
                if u_in not in db["h_id"]: db["h_id"].append(u_in)
                st.rerun()
            except: st.error("Gagal")

# --- MONITORING ---
st.title("Monitor 16:10 Pro")

for g_name, g_data in db["groups"].items():
    if g_data["members"]:
        st.subheader(f"📍 {g_name}")
        uids = list(g_data["members"].keys())
        
        try:
            r = requests.post("https://presence.roblox.com/v1/presence/users", 
                             json={"userIds": uids}, timeout=5).json()
            pres = {str(p['userId']): p['userPresenceType'] for p in r.get('userPresences', [])}
            
            # MEMBUAT GRID 4 KOLOM
            cols = st.columns(4)
            for i, uid in enumerate(uids):
                info = g_data["members"][uid]
                curr = pres.get(uid, 0)
                
                # NOTIF KELUAR GAME SAJA (Status 2 pindah ke bukan 2)
                if info["last"] == 2 and curr != 2 and info["last"] != -1:
