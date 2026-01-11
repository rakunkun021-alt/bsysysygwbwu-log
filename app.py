import streamlit as st
import requests
import time
import json

# --- CONFIG & UI STYLE ---
st.set_page_config(page_title="Roblox Monitor 16:10", layout="wide")

# CSS untuk Rasio 16:10, Indikator Samping Nama, dan Grid 4 Kolom
st.markdown("""
    <style>
    /* Paksa Grid 4 Kolom di Mobile */
    div[data-testid="stColumn"] {
        flex: 1 1 23% !important;
        min-width: 85px !important;
        padding: 3px !important;
    }
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
    }
    
    /* Box Rasio 16:10 */
    .card-roblox {
        border: 1px solid #444;
        border-radius: 6px;
        background-color: #1a1c24;
        padding: 8px;
        aspect-ratio: 16 / 10; /* Rasio lebar ke tinggi */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        overflow: hidden;
    }
    
    /* Indikator Samping Nama */
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
        display: inline-block;
        flex-shrink: 0;
    }
    .online { background-color: #2ecc71; box-shadow: 0 0 5px #2ecc71; }
    .offline { background-color: #e74c3c; }
    
    .username-text {
        font-size: 11px;
        font-weight: bold;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        color: white;
    }
    .id-text { font-size: 9px; color: #888; }
    
    /* Tombol Hapus Kecil */
    .stButton > button {
        width: 100% !important;
        height: 20px !important;
        font-size: 10px !important;
        padding: 0px !important;
        margin-top: 4px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def send_telegram(token, chat_id, message):
    if not token or not chat_id: return
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                      json={"chat_id": chat_id, "text": message}, timeout=5)
    except: pass

# --- DATABASE SESSION ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "groups": {"Utama": {"token": "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k", "chat_id": "8170247984", "members": {}}},
        "h_id": [], "h_tk": ["8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k"], "h_ci": ["8170247984"]
    }

db = st.session_state.db

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Admin")
    
    # Fitur Anti Hilang
    with st.expander("💾 Backup Data (Anti Hilang)"):
        st.caption("Salin kode ini ke catatan HP:")
        st.code(json.dumps(db))
        restore = st.text_input("Restore (Tempel kode):")
        if st.button("Restore"):
            try:
                st.session_state.db = json.loads(restore)
                st.rerun()
            except: st.error("Format Salah")

    with st.expander("🤖 Set Bot & Grup"):
        gn = st.text_input("Grup:")
        tk = st.selectbox("Riwayat Token:", options=db["h_tk"])
        tk_n = st.text_input("Token Baru:")
        ci = st.selectbox("Riwayat Chat ID:", options=db["h_ci"])
        ci_n = st.text_input("Chat ID Baru:")
        if st.button("Simpan Grup"):
            ft, fc = (tk_n if tk_n else tk), (ci_n if ci_n else ci)
            db["groups"][gn] = {"token": ft, "chat_id": fc, "members": {}}
            if ft not in db["h_tk"]: db["h_tk"].append(ft)
            if fc not in db["h_ci"]: db["h_ci"].append(fc)
            st.rerun()

    st.divider()
    target = st.selectbox("Ke Grup:", list(db["groups"].keys()))
    h_sel = st.selectbox("Riwayat ID:", options=["-- Baru --"] + db["h_id"])
    u_in = st.text_input("ID Roblox:", value="" if h_sel == "-- Baru --" else h_sel)

    if st.button("Add ID"):
        if u_in.isdigit():
            try:
                res = requests.get(f"https://users.roblox.com/v1/users/{u_in}").json()
                name = res.get('name', f"User-{u_in}")
                db["groups"][target]["members"][u_in] = {"name": name, "last": -1}
                if u_in not in db["h_id"]: db["h_id"].append(u_in)
                st.rerun()
            except: st.error("Error")

# --- MAIN UI ---
st.title("🎮 Roblox Live Monitor")

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
                dot_class = "online" if curr == 2 else "offline"
                
                with cols[i % 4]:
                    st.markdown(f"""
                    <div class="card-roblox">
                        <div class="user-row">
                            <span class="status-dot {dot_class}"></span>
                            <span class="username-text">{name}</span>
                        </div>
                        <div class="id-text">{uid}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Hapus", key=f"d_{g_name}_{uid}"):
                        del db["groups"][g_name]["members"][uid]
                        st.rerun()
        except: st.write("Loading...")

time.sleep(30)
st.rerun()
