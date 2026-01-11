import streamlit as st
import requests, time, json, os

# --- DATABASE PERMANEN ---
DB = "monitor_db.json"
def load():
    if os.path.exists(DB):
        try:
            with open(DB, "r") as f: return json.load(f)
        except: return {"groups": {}, "h_tk": [], "h_id": []}
    return {"groups": {}, "h_tk": [], "h_id": []}

def save(d):
    with open(DB, "w") as f: json.dump(d, f)

if 'db' not in st.session_state: st.session_state.db = load()
db = st.session_state.db

# --- UI CONFIG (VIEW LIST SEPERTI WINDOWS EXPLORER) ---
st.set_page_config(page_title="Monitor List", layout="wide")
st.markdown("""
<style>
    .block-container { padding: 0.5rem !important; }
    
    /* Paksa 4 Kolom List berjejer */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 4px !important;
    }
    [data-testid="column"] {
        flex: 1 1 25% !important;
        min-width: 0 !important;
    }

    /* Style View List (Windows Explorer Style) */
    .list-item {
        border: 1px solid #333;
        background: #1e1e1e;
        display: flex;
        align-items: center;
        padding: 4px 6px;
        border-radius: 2px;
        height: 30px; /* Pendek seperti list */
        overflow: hidden;
    }
    
    .dot { height: 8px; width: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; flex-shrink: 0; }
    .on { background: #00ff00; box-shadow: 0 0 5px #00ff00; }
    .off { background: #ff0000; }
    
    .text-container { display: flex; flex-direction: column; overflow: hidden; }
    .u-n { font-size: 10px; font-weight: bold; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .u-i { font-size: 8px; color: #888; line-height: 1; }

    /* Tombol Sampah di samping list */
    .stButton>button {
        width: 100% !important;
        height: 20px !important;
        font-size: 10px !important;
        background: transparent !important;
        border: 1px solid #444 !important;
        margin-top: 2px !important;
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

def notify(tk, ci, msg):
    if tk and ci:
        try: requests.post("https://api.telegram.org/bot"+tk+"/sendMessage", json={"chat_id":ci,"text":msg}, timeout=5)
        except: pass

# --- SIDEBAR ---
with st.sidebar:
    st.header("Admin")
    with st.expander("Grup"):
        gn, tk, ci = st.text_input("Nama"), st.text_input("Token"), st.text_input("ID Chat")
        if st.button("Simpan"):
            if gn and tk:
                db["groups"][gn] = {"tk":tk, "ci":ci, "members":{}}
                if tk not in db["h_tk"]: db["h_tk"].append(tk)
                save(db); st.rerun()

    if db["groups"]:
        st.divider()
        target = st.selectbox("Pilih Grup", list(db["groups"].keys()))
        uid = st.text_input("ID Roblox")
        
        # Logika Indikator O Hijau / X Merah
        if uid:
            if uid.isdigit():
                st.markdown("<span style='color:#00ff00;'>●</span> ID Valid", unsafe_allow_html=True)
            else:
                st.markdown("<span style='color:#ff0000;'>x</span> Masukkan Angka", unsafe_allow_html=True)

        if st.button("Tambah ID"):
            if uid.isdigit():
                try:
                    r = requests.get("https://users.roblox.com/v1/users/"+uid, headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
                    if r.status_code == 200:
                        db["groups"][target]["members"][uid] = {"name": r.json().get("name", uid), "last":-1}
                        if uid not in db["h_id"]: db["h_id"].append(uid)
                        save(db)
                        st.toast("ID Berhasil Ditambah", icon="✅")
                        time.sleep(1)
                        st.rerun()
                except: st.error("API Error")

    with st.expander("Riwayat"):
        for hid in db["h_id"]:
            c1, c2 = st.columns([3,1])
            c1.text(hid)
            if c2.button("❌", key="h"+hid):
                db["h_id"].remove(hid); save(db); st.rerun()

# --- MAIN DASHBOARD ---
st.title("Roblox Monitor List")
for gn, info in db["groups"].items():
    with st.expander(gn, expanded=True):
        if not info["members"]: continue
        uids = list(info["members"].keys())
        try:
            res = requests.post("https://presence.roblox.com/v1/presence/users", json={"userIds":uids}, timeout=10).json()
            pres = {str(p['userId']): p['userPresenceType'] for p in res.get('userPresences', [])}
            
            for j in range(0, len(uids), 4):
                cols = st.columns(4)
                for i, uid_user in enumerate(uids[j:j+4]):
                    m = info["members"][uid_user]
                    cur = pres.get(uid_user, 0)
                    
                    if m.get("last") == 2 and cur != 2 and m.get("last") != -1:
                        notify(info["tk"], info["ci"], "🔴 "+m['name']+" KELUAR")
                    
                    db["groups"][gn]["members"][uid_user]["last"] = cur
                    save(db)
                    
                    with cols[i]:
                        st.markdown(f'''
                        <div class="list-item">
                            <span class="dot {"on" if cur==2 else "off"}"></span>
                            <div class="text-container">
                                <div class="u-n">{m["name"]}</div>
                                <div class="u-i">{uid_user}</div>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                        if st.button("🗑️", key="d"+gn+uid_user):
                            del db["groups"][gn]["members"][uid_user]; save(db); st.rerun()
        except: pass

time.sleep(15)
st.rerun()
