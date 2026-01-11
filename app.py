import streamlit as st
import requests
import time
import json
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Roblox Monitor V2", layout="wide")

# --- SISTEM PENYIMPANAN PERMANEN (JSON) ---
DB_FILE = "roblox_db.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {
        "groups": {},
        "history_tokens": [],
        "history_ids": []
    }

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# Inisialisasi Data
if 'db' not in st.session_state:
    st.session_state.db = load_data()

db = st.session_state.db

# --- CSS: KUNCI 4 KOLOM & 16:10 ---
st.markdown("""
<style>
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 10px !important;
    }
    [data-testid="column"] {
        flex: 0 0 calc(25% - 10px) !important;
        min-width: calc(25% - 10px) !important;
    }
    .card-roblox {
        border: 1px solid #333;
        border-radius: 10px;
        background: #111;
        aspect-ratio: 16 / 10;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 10px;
    }
    .dot { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin-right: 5px; }
    .online { background-color: #2ecc71; box-shadow: 0 0 8px #2ecc71; }
    .offline { background-color: #e74c3c; }
    .name { color: white; font-weight: bold; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

def send_alert(token, chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                      json={"chat_id": chat_id, "text": text}, timeout=5)
    except: pass

# --- SIDEBAR: MANAGEMENT ---
with st.sidebar:
    st.title("🛡️ Admin Panel")
    
    # 1. FITUR GRUP TANPA BATAS
    with st.expander("➕ Buat Grup Baru"):
        new_g_name = st.text_input("Nama Grup:")
        new_g_token = st.text_input("Token Bot Telegram:")
        new_g_chat = st.text_input("Chat ID Telegram:")
        if st.button("Simpan Grup"):
            if new_g_name and new_g_token:
                db["groups"][new_g_name] = {"token": new_g_token, "chat_id": new_g_chat, "members": {}}
                if new_g_token not in db["history_tokens"]: db["history_tokens"].append(new_g_token)
                save_data(db)
                st.rerun()

    # 2. RIWAYAT TOKEN
    if db["history_tokens"]:
        with st.expander("📜 Riwayat Token"):
            for t in db["history_tokens"]:
                st.code(t)
                if st.button("Hapus Token", key=f"del_tk_{t}"):
                    db["history_tokens"].remove(t)
                    save_data(db)
                    st.rerun()

    st.divider()

    # 3. INPUT ID KE GRUP
    if db["groups"]:
        target_g = st.selectbox("Pilih Grup Tujuan:", list(db["groups"].keys()))
        u_id = st.text_input("Masukkan ID Roblox:")
        if st.button("Tambah ID"):
            if u_id.isdigit():
                res = requests.get(f"https://users.roblox.com/v1/users/{u_id}").json()
                name = res.get("name", f"User-{u_id}")
                db["groups"][target_g]["members"][u_id] = {"name": name, "last": -1}
                if u_id not in db["history_ids"]: db["history_ids"].append(u_id)
                save_data(db)
                st.rerun()

    # 4. RIWAYAT ID PERMANEN
    with st.expander("👥 Riwayat ID Pernah Diinput"):
        for hid in db["history_ids"]:
            col_a, col_b = st.columns([3, 1])
            col_a.text(hid)
            if col_b.button("❌", key=f"h_id_{hid}"):
                db["history_ids"].remove(hid)
                save_data(db)
                st.rerun()

# --- MAIN DASHBOARD ---
st.title("🎮 Monitoring Live")

for g_name, g_info in db["groups"].items():
    st.header(f"Group: {g_name}")
    if not g_info["members"]:
        st.info("Belum ada
