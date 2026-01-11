import streamlit as st
import requests, time, json, os

# --- DATABASE PERMANEN ---
DB = "monitor_db.json"

def load_data():
    if os.path.exists(DB):
        try:
            with open(DB, "r") as f:
                d = json.load(f)
                # Pastikan kunci utama selalu ada
                for k in ["groups", "h_id"]:
                    if k not in d: d[k] = [] if k == "h_id" else {}
                return d
        except: pass
    return {"groups": {}, "h_id": []}

def save_data(d):
    with open(DB, "w") as f:
        json.dump(d, f, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = load_data()
db = st.session_state.db

# --- UI CONFIG ---
st.set_page_config(page_title="Roblox Monitor", layout="wide")
st.markdown("""
<style>
    .block-container { padding: 0.5rem !important; }
    
    /* Perbaikan Tombol agar tidak terpotong ke bawah */
    .stButton>button {
        width: 100% !important;
        white-space: nowrap !important;
        display: block !important;
        min-height: 40px !important;
    }

    /* List Item Horizontal */
    .list-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #1e1e1e;
        border: 1px solid #333;
        padding: 8px 12px;
        border-radius: 5px;
        margin-bottom: 5px;
    }
    
    .user-box { display: flex; align-items: center; gap: 10px; flex-grow: 1; }
    .dot { height: 10px; width: 10px; border-radius: 50%; display: inline-block; }
    .on { background: #0f0; box-shadow: 0 0 5px #0f0; }
    .off { background: #f00; }
    .u-n { font-size: 14px; font-weight: bold; color: #fff; }

    /* Tombol Sampah Khusus */
    .btn-del > div > button {
        background: transparent !important;
        border: none !important;
        color: #ff4b4b !important;
        font-size: 20px !important;
        min-height: unset !important;
        height: 30px !
