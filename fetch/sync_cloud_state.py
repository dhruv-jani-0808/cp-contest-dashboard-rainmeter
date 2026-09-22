"""
CP Dashboard - Cloud State Synchronizer.
Reads live ShowLC and ShowGFG checkbox states from the active Rainmeter skin
and uploads them to Ntfy.sh's state bucket.
"""

import sys
import os
import json
import urllib.request
from datetime import datetime

# Reconfigure stdout to handle UTF-8 characters safely on Windows CMD/PowerShell
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

STATE_TOPIC = "dhruv_potd_state_bucket"
STATE_URL = f"https://ntfy.sh/{STATE_TOPIC}"

def find_variables_path():
    appdata = os.environ.get('APPDATA', '')
    ini_path = os.path.join(appdata, 'Rainmeter', 'Rainmeter.ini')
    if os.path.exists(ini_path):
        try:
            with open(ini_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.strip().startswith('SkinPath='):
                        skin_dir = line.strip().split('=', 1)[1].strip()
                        active_vars = os.path.join(skin_dir, 'CPDashboard', 'variables.inc')
                        if os.path.exists(active_vars):
                            return active_vars
        except Exception:
            pass

    onedrive_vars = os.path.expanduser('~/OneDrive/Documents/Rainmeter/Skins/CPDashboard/variables.inc')
    if os.path.exists(onedrive_vars):
        return onedrive_vars

    doc_vars = os.path.expanduser('~/Documents/Rainmeter/Skins/CPDashboard/variables.inc')
    if os.path.exists(doc_vars):
        return doc_vars

    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(script_dir, "../rainmeter/variables.inc"))

def load_variables(filepath):
    vars_dict = {}
    if not os.path.exists(filepath):
        return vars_dict
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith(';') and not line.startswith('['):
                if '=' in line:
                    key, val = line.split('=', 1)
                    vars_dict[key.strip()] = val.strip()
    return vars_dict

def sync_to_cloud():
    variables_path = find_variables_path()
    config = load_variables(variables_path)
    
    show_lc = config.get("ShowLC", "1")
    show_gfg = config.get("ShowGFG", "1")
    ntfy_topic = config.get("NtfyTopic", "dhruv_potd_streak")
    
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    payload = {
        "date": today_date,
        "show_lc": int(show_lc),
        "show_gfg": int(show_gfg),
        "ntfy_topic": ntfy_topic,
        "updated_at": datetime.now().isoformat()
    }
    
    data = json.dumps(payload).encode('utf-8')
    headers = {
        "Title": "state_update",
        "Tags": "state",
        "User-Agent": "CPDashboard-StateSync/2.2"
    }
    req = urllib.request.Request(STATE_URL, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res = response.read().decode('utf-8')
            print(f"[+] Ntfy Cloud State Sync Successful: Date={today_date}, LC={show_lc}, GFG={show_gfg}")
            return True
    except Exception as e:
        print(f"[-] Error uploading cloud sync state: {e}")
        return False

if __name__ == "__main__":
    sync_to_cloud()
