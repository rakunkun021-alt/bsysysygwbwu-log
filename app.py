import streamlit as st
import requests
import time
import json

# --- CONFIG ---
st.set_page_config(page_title="Roblox Monitor 16:10", layout="wide")

# CSS UNTUK GRID 4 KOLOM & RASIO 16:10
st.markdown("""
<style>
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 12px !important;
    }
    [data-testid="column"] {
        flex: 0 0 calc(25% - 15px) !important;
        min-width: 150px !important;
        margin-bottom: 15px !important;
    }
    .card-roblox {
        border: 1px solid #444;
        border-radius: 10px;
        background-color: #1a1c24;
        padding: 15px;
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
        gap: 8px;
        margin-bottom: 5px;
    }
    .status-dot { height: 12px; width: 12px; border-radius: 50%; }
    .online { background-color: #2ecc71; box-shadow: 0 0 8px #2ecc71; }
    .offline { background-color: #e74c3c; }
    .username-text { font-size: 14px; font-weight: bold; color: white; }
    .id-text { font-size: 11px; color: #888; }
    .stButton > button {
        width: 100% !important;
        height: 28px !important;
        font-size: 11px !important;
    }
</style>
""", unsafe_allow_html=True)

def send_telegram(token, chat_id, message):
    if not token or not chat_id: return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=5)
    except: pass

# --- SESSION DATABASE (ANTI HILANG) ---
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
    st.header("⚙️ Admin Panel")
    with st.expander("💾 Backup & Restore"):
        st.code(json.dumps(db))
        res_code = st.text_area("Tempel kode restore:")
        if st.button("Restore Now"):
            try:
                st.session_state.db = json.loads(res_code)
                st.rerun()
            except: st.error("Gagal")
    
    st.divider()
    target = st.selectbox("Pilih Grup:", list(db["groups"].keys()))
    u_in = st.text_input("Input ID Roblox:")
    if st.button("Tambahkan"):
        if u_in.isdigit():
            try:
                res = requests.get(f"https://users.roblox.com/v1/users/{u_in}").json()
                name = res.get('name', f"User-{u_in}")
                # Status awal -1 agar tidak kirim notif palsu
                db["groups"][target]["members"][u_in] = {"name": name, "last": -1}
                if u_in not in db["h_id"]: db["h_id"].append(u_in)
                st.rerun()
            except: st.error("ID Gagal")

# --- MONITORING ---
st.title("Roblox Monitor 16:10")

for g_name, g_data in db["groups"].items():
    if g_data["members"]:
        st.subheader(f"📍 {g_name}")
        uids = list(g_data["members"].keys())
        
        try:
            r = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}, timeout=5).json()
            pres = {str(p['userId']): p['userPresenceType'] for p in r.get('userPresences', [])}
            
            # GRID 4 KOLOM
            cols = st.columns(4)
            for i, uid in enumerate(uids):
                info = g_data["members"][uid]
                curr = pres.get(uid, 0)
                
                # HANYA NOTIF KELUAR GAME (Status 2 ke bukan 2)
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
                    """, unsafe_allow_html=True)
                    if st.button(f"Hapus {uid}", key=f"del_{uid}"):
                        del db["groups"][g_name]["members"][uid]
                        st.rerun()
        except: st.write("Refreshing...")

time.sleep(15)
st.rerun()
