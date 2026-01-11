import streamlit as st
import requests
import time
import json

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Roblox Monitor 16:10", layout="wide")

# CSS KHUSUS UNTUK MEMAKSA 4 KOLOM DI HP & RASIO 16:10
st.markdown("""
<style>
    /* Paksa kolom tetap berjejer ke samping (tidak menumpuk) di HP */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        align-items: flex-start !important;
        justify-content: flex-start !important;
        gap: 8px !important;
    }

    /* Kunci lebar tiap kolom agar pas 4 per baris */
    [data-testid="column"] {
        width: calc(25% - 8px) !important;
        flex: 0 0 calc(25% - 8px) !important;
        min-width: calc(25% - 8px) !important;
    }

    /* Box Monitoring Rasio 16:10 */
    .card-roblox {
        border: 1px solid #444;
        border-radius: 8px;
        background-color: #1a1c24;
        padding: 10px 5px;
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
        gap: 5px;
        width: 100%;
    }

    .status-dot { 
        height: 10px; 
        width: 10px; 
        border-radius: 50%; 
        flex-shrink: 0;
    }
    .online { background-color: #2ecc71; box-shadow: 0 0 5px #2ecc71; }
    .offline { background-color: #e74c3c; }

    .username-text { 
        font-size: 11px; 
        font-weight: bold; 
        color: white;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .id-text { font-size: 9px; color: #888; }

    /* Tombol Hapus agar kecil dan rapi di bawah kartu */
    .stButton > button {
        width: 100% !important;
        height: 24px !important;
        font-size: 9px !important;
        padding: 0px !important;
        margin-top: 4px !important;
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
st.title("Roblox Monitor Pro")

for g_name, g_data in db["groups"].items():
    if g_data["members"]:
        st.subheader(f"📍 {g_name}")
        uids = list(g_data["members"].keys())
        
        try:
            r = requests.post("https://presence.roblox.com/v1/presence/users", 
                             json={"userIds": uids}, timeout=5).json()
            pres = {str(p['userId']): p['userPresenceType'] for p in r.get('userPresences', [])}
            
            # MEMBUAT GRID 4 KOLOM (Paksa ke samping)
            cols = st.columns(4)
            for i, uid in enumerate(uids):
                info = g_data["members"][uid]
                curr = pres.get(uid, 0)
                
                # NOTIF KELUAR GAME SAJA
                if info["last"] == 2 and curr != 2 and info["last"] != -1:
                    send_telegram(g_data["token"], g_data["chat_id"], f"🔴 {info['name']} KELUAR GAME")
                
                db["groups"][g_name]["members"][uid]["last"] = curr
                dot = "online" if curr == 2 else "offline"
                
                with cols[i % 4]:
                    st.markdown(f"""
                    <div class="card-roblox">
                        <div class="user-row">
                            <div class="status-dot {dot}"></div>
                            <div class="username-text">{info['name']}</div>
                        </div>
                        <div class="id-text">{uid}</div>
                    </div>
                    """, unsafe
