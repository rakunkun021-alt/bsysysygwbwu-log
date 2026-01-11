import streamlit as st
import requests, time, json, os

# --- DATABASE ---
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

# --- UI CONFIG (VIEW LIST & TRASH ASIDE) ---
st.set_page_config(page_title="Monitor List", layout="wide")
st.markdown("""
<style>
    .block-container { padding: 0.5rem !important; }
    
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 3px !important;
    }
    [data-testid="column"] {
        flex: 1 1 25% !important;
        min-width: 0 !important;
    }

    /* Windows List Style */
    .list-container {
        display: flex;
        align-items: center;
        border: 1px solid #333;
        background: #1e1e1e;
        padding: 2px 5px;
        border-radius: 2px;
        height: 28px;
        justify-content: space-between;
    }
    
    .user-info { display: flex; align-items: center; overflow: hidden; }
    .dot { height: 7px; width: 7px; border-radius: 50%; display: inline-block; margin-right: 5px; flex-shrink: 0; }
    .on { background: #00ff00; box-shadow: 0 0 4px #00ff00; }
    .off { background: #ff0000; }
    
    .u-n { font-size: 9px; font-weight: bold; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis
