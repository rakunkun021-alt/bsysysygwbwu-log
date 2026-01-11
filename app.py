import streamlit as st
import requests, time, json, os

DB_FILE = "monitor_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {"groups": {}, "h_tk": [], "h_id": []}
    return {"groups": {}, "h_tk": [], "h_id": []}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

if 'db' not in st.session_state:
    st.session_state.db = load_db()
db = st.session_state.db

st.set_page_config(page_title="Monitor 16:10", layout="wide")
st.markdown("""
<style>
    .block-container { padding: 0.5rem !important; }
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: wrap !important; gap: 4px !important; }
    [data-testid="column"] { width: calc(25% - 4px) !important; flex: 0 0 calc(25% - 4px) !important; min-width: 60px !important; margin-bottom: 4px !important; }
    .card { border: 1px solid #444; border-radius: 4px; background: #1a1c24; aspect-ratio: 16/10; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 2px; }
    .dot { height: 6px; width: 6px; border-radius: 50%; display: inline-block; margin-right: 2px; }
    .on { background: #2ecc71; box-shadow: 0 0 4px #2ecc71; }
    .off { background: #e74c3c; }
    .u-n { font-size: 8px; font-weight: bold; color: white; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 95%; }
    .u-i { font-size: 6px; color
