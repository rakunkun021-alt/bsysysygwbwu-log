import streamlit as st
import requests
import time
import json

# --- CONFIG & UI STYLE ---
st.set_page_config(page_title="Roblox Monitor", layout="wide")

# CSS UNTUK GRID KONSISTEN & RASIO 16:10
st.markdown("""
    <style>
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 5px !important;
        justify-content: flex-start !important;
    }
    /* Memaksa kolom tetap 25% lebar layar (4 per baris) */
    [data-testid="column"] {
        flex: 1 1 calc(25% - 10px) !important;
        min-width: 80px !important;
        max-width: calc(25% - 10px) !important;
        padding: 0px !important;
        margin-bottom: 10px !important;
    }
    .card-roblox {
        border: 1px solid #444;
        border-radius: 6px;
        background-color: #1a1c24;
        padding: 8px;
        aspect-ratio: 16 / 10;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }
    .user-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
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
    .id-text { font-size: 9px; color: #888; margin-top: 2px; }
    .stButton > button {
        width: 100% !important;
        height: 22px !important;
        font-size: 10px !important;
        padding: 0px !important;
        margin-top: 2px !important;
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
    
    with st.expander("💾 Backup & Restore (Anti Hilang)"):
        st.caption("Salin kode ini ke Catatan HP:")
        st.code(json.dumps(db))
        restore = st.text_input("Tempel kode restore di sini:")
        if st.button("Restore Sekarang"):
            try:
                st.session_state.db = json.loads(restore)
                st.rerun()
            except:
                st.error("Kode salah")

    with st.expander("🤖 Set Bot & Grup"):
        gn = st.text_input("Nama Grup Baru:")
        tk_sel = st.selectbox("Riwayat Token:", options=db["h_tk"])
        tk_new = st.text_input("Ketik Token Baru:")
        ci_sel = st.selectbox("Riwayat Chat ID:", options=db["h_ci"])
        ci_new = st.text_input("Ketik Chat ID Baru:")
        if st.button("Simpan Konfigurasi"):
            if gn:
                ft = tk_new if tk_new else tk_sel
                fc = ci_new if ci_new else ci_sel
                db["groups"][gn] = {"token": ft, "chat_id": fc, "members": {}}
                if ft not in db["h_tk"]: db["h_tk"].append(ft)
                if fc not in db["h_ci"]: db["h_ci"].append(fc)
                st.rerun()

    st.divider()
    target = st.selectbox("Pilih Grup:", list(db["groups"].keys()))
    h_sel = st.selectbox("Riwayat ID:", options=["-- Baru --"] + db["h_id"])
    u_in = st.text_input("Input ID Roblox:", value="" if h_sel == "-- Baru --" else h_sel)

    if st.button("Tambahkan"):
        if u_in.isdigit():
            try:
                res = requests.get(f"https://users.roblox.com/v1/users/{u_in}").json()
                name = res.get('name', f"User-{u_in}")
                db["groups"][target]["members"][u_in] = {"name": name, "last": -1}
                if u_in not in db["h_id"]: db["h_id"].append(u_in)
                st.rerun()
            except:
                st.error("Error")

# --- MAIN UI ---
st.title("Live Monitor")

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
                dot_color = "online" if curr == 2 else "offline"
                
                with cols[i % 4]:
                    st.markdown(f"""
                    <div class="card-roblox">
                        <div class="user-row">
                            <span class="status-dot {dot_color}"></span>
                            <span class="username-text">{name}</span>
                        </div>
                        <div class="id-text">{uid}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_{g_name}_{uid}"):
                        del db["groups"][g_name]["members"][uid]
                        st.rerun()
        except:
            st.write("Refreshing...")

time.sleep(30)
st.rerun()
