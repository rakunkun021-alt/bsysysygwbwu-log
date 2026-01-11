import streamlit as st
import requests, time, json

# --- CONFIG & CSS ---
st.set_page_config(page_title="Monitor 16:10", layout="wide")
st.markdown("""
<style>
    /* Paksa 4 kolom tetap berjejer ke samping di HP */
    [data-testid="stHorizontalBlock"] { 
        display: flex !important; flex-direction: row !important; flex-wrap: wrap !important; gap: 6px !important; 
    }
    /* Kunci lebar kolom 25% agar 1 baris isi 4 ID */
    [data-testid="column"] { 
        width: calc(25% - 10px) !important; flex: 0 0 calc(25% - 10px) !important; min-width: calc(25% - 10px) !important; margin-bottom: 8px !important; 
    }
    /* Box Rasio 16:10 */
    .card { 
        border: 1px solid #444; border-radius: 6px; background: #1a1c24; padding: 10px 4px; aspect-ratio: 16 / 10; 
        display: flex; flex-direction: column; justify-content: center; align-items: center; 
    }
    .row { display: flex; align-items: center; gap: 4px; width: 100%; justify-content: center; }
    .dot { height: 8px; width: 8px; border-radius: 50%; }
    .on { background: #2ecc71; box-shadow: 0 0 5px #2ecc71; }
    .off { background: #e74c3c; }
    .u-text { font-size: 10px; font-weight: bold; color: white; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .id-t { font-size: 8px; color: #888; }
    .stButton>button { width: 100% !important; height: 22px !important; font-size: 8px !important; padding: 0 !important; margin-top: 4px !important; }
</style>
""", unsafe_allow_html=True)

def send_tg(tk, ci, msg):
    if tk and ci:
        try: requests.post(f"https://api.telegram.org/bot{tk}/sendMessage", json={"chat_id":ci, "text":msg}, timeout=5)
        except: pass

# --- DATABASE ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "groups": {
            "Utama": {
                "tk": "8243788772:AAGrR-XFydCLZKzykofsU8qYXhkXg26qt2k", 
                "ci": "8170247984", 
                "members": {}
            }
        }
    }
db = st.session_state
