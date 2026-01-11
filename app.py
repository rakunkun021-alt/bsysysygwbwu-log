import streamlit as st
import requests
import time
import json

# --- CONFIG & UI STYLE ---
st.set_page_config(page_title="Roblox Monitor 16:10", layout="wide")

# CSS UNTUK GRID KONSISTEN & RASIO 16:10
st.markdown("""
    <style>
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 5px !important;
        justify-content: flex-start !important;
    }
    /* Memaksa kolom tetap 24% agar muat 4 per baris dan tidak melar */
    [data-testid="column"] {
        flex: 0 0 24% !important;
        min-width: 80px !important;
        max-width: 24% !important;
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
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        requests.post(url, json=payload, timeout=5)
    except:
        pass

# --- DATABASE SESSION ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "groups": {"Utama": {"token": "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k", "chat_id": "8170247984", "members": {}}},
        "h_id": [], 
        "h_tk": ["8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k"], 
        "h_ci": ["8170247984"]
    }

db = st.session_state.db

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Admin Panel")
    
    with st.expander("💾 Backup & Restore (Anti Hilang)"):
        st.caption("Salin kode ini ke Catatan HP:")
        st.code(json.dumps(db))
        restore_code = st.text_input("Tempel kode restore di sini:")
        if st.button("Restore Sekarang"):
            if restore_code:
                try:
                    st.session_state.db = json.loads(restore_code)
                    st.rerun()
                except:
                    st.error("Format kode salah")

    with st.expander("🤖 Set Bot & Grup"):
        gn = st.text_input("Nama Grup Baru:")
        tk_sel = st.selectbox("Riwayat Token:", options=db["h_tk"])
        tk_new = st.text_input("Atau Token Baru:")
        ci_sel = st.selectbox("Riwayat Chat ID:", options=db["h_ci"])
        ci_new = st.text_input("Atau Chat ID Baru:")
        
        if st.button("Simpan Konfigurasi"):
            if gn:
                ft = tk_new if tk_new else tk_sel
                fc = ci_new if ci_new else ci_sel
                db["groups"][gn] = {"token": ft, "chat_id": fc, "members": {}}
                if ft and ft not in db["h_tk"]: db["h_tk"].append(ft)
                if fc and fc not in db["h_ci"]: db["h_ci"].append(fc)
                st.rerun()

    st.divider()
    target_grp = st.selectbox("Pilih Grup:", list(db["groups"].keys()))
    h_sel_id = st.selectbox("Riwayat User ID:", options=["-- Baru --"] + db["h_id"])
    u_input_id = st.text_input("Input ID Roblox:", value="" if h_sel_id == "-- Baru --" else h_sel_id)

    if st.button("Tambahkan"):
        if u_input_id.isdigit():
            try:
                res_u = requests.get(f"https://users.roblox.com/v1/users/{u_input_id}").json()
                u_name = res_u.get('name', f"User-{u_input_id}")
                db["groups"][target_grp]["members"][u_input_id] = {"name": u_name, "last": -1}
                if u_input_id not in db["h_id"]: db["h_id"].append(u_input_id)
                st.rerun()
            except:
                st.error("Gagal")

# --- MAIN UI ---
st.title("Roblox Monitor")

for g_name, g_data in db["groups"].items():
    if g_data["members"]:
        st.subheader(f"📍 {g_name}")
        uids = list(g_data["members"].keys())
        
        try:
            r_pres = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds": uids}).json()
            pres_map = {str(p['userId']): p['userPresenceType'] for p in r_pres.get('userPresences', [])}
            
            # Grid 4 Kolom
            cols = st.columns(4)
            for i, uid in enumerate(uids):
                curr_s = pres_map.get(uid, 0)
                old_s = g_data["members"][uid]["last"]
                u_n = g_data["members"][uid]["name"]
                
                if old_s == 2 and curr_s != 2:
                    send_telegram(g_data["token"], g_data["chat_id"], f"🔴 {u_n} Keluar Game")
                
                db["groups"][g_name]["members"][uid]["last"] = curr_s
                dot_c = "online" if curr_s == 2 else "offline"
                
                with cols[i % 4]:
                    st.markdown(f"""
                    <div class="card-roblox">
                        <div class="user-row">
                            <span class="status-dot {dot_c}"></span>
                            <span class="username-text">{u_n}</span>
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
