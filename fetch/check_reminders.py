"""
CP Dashboard - Ntfy.sh Daily POTD / Streak Reminder Script.
Checks if ShowLC or ShowGFG checkboxes are unticked (0) in variables.inc,
and sends an instant phone push notification (8:00 PM) or an urgent loud alarm alert (10:00 PM) via Ntfy.sh.
"""

import sys
import os
import argparse
import urllib.request
import urllib.parse
from datetime import datetime

# Reconfigure stdout to handle UTF-8 characters safely on Windows CMD/PowerShell
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def find_variables_path():
    """
    Finds the active Rainmeter skins folder's variables.inc first,
    where Rainmeter writes live checkbox clicks.
    """
    # 1. Try reading Rainmeter.ini to get active SkinPath
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

    # 2. Check OneDrive / User Documents path
    onedrive_vars = os.path.expanduser('~/OneDrive/Documents/Rainmeter/Skins/CPDashboard/variables.inc')
    if os.path.exists(onedrive_vars):
        return onedrive_vars

    doc_vars = os.path.expanduser('~/Documents/Rainmeter/Skins/CPDashboard/variables.inc')
    if os.path.exists(doc_vars):
        return doc_vars

    # 3. Fallback to local repo directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(script_dir, "../rainmeter/variables.inc"))

def load_variables(filepath):
    """
    Parses key-value pairs from Rainmeter variables.inc file.
    """
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

def send_ntfy_notification(topic, title, message, priority="3", tags="warning"):
    if not topic:
        topic = "dhruv_potd_streak"
        
    url = f"https://ntfy.sh/{urllib.parse.quote(topic)}"
    
    # Ensure header values are ASCII safe for urllib
    safe_title = title.encode('ascii', 'ignore').decode('ascii')
    
    headers = {
        "Title": safe_title,
        "Priority": str(priority),
        "Tags": tags,
        "User-Agent": "CPDashboard-Reminder/2.2"
    }
    
    data = message.encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res = response.read().decode('utf-8')
            print(f"[+] Ntfy.sh Notification Sent Successfully (Topic: {topic}): {res}")
            return True
    except Exception as e:
        print(f"[-] Error sending Ntfy.sh alert: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Check CP Dashboard POTD streak reminders via Ntfy.sh.")
    parser.add_argument("--type", choices=["whatsapp", "call"], default="whatsapp", help="Type of reminder to send.")
    args = parser.parse_args()

    variables_path = find_variables_path()
    config = load_variables(variables_path)
    
    show_lc = config.get("ShowLC", "1")
    show_gfg = config.get("ShowGFG", "1")
    ntfy_topic = config.get("NtfyTopic", "dhruv_potd_streak")
    
    print(f"[{datetime.now().isoformat()}] Reading config from: {variables_path}")
    print(f"    - ShowLC: {show_lc}, ShowGFG: {show_gfg}")
    
    # Check if either checkbox is unticked (0)
    if show_lc == "0" or show_gfg == "0":
        unticked_list = []
        if show_lc == "0":
            unticked_list.append("LeetCode")
        if show_gfg == "0":
            unticked_list.append("GFG")
            
        platforms_str = " and ".join(unticked_list)
        
        if args.type == "whatsapp":
            title = "POTD Streak Reminder (8:00 PM)"
            message = f"You haven't completed your {platforms_str} problem of the day today!"
            print(f"[+] Sending 8:00 PM Ntfy alert for {platforms_str}...")
            send_ntfy_notification(ntfy_topic, title, message, priority="3", tags="warning,memo")
        elif args.type == "call":
            title = "URGENT POTD STREAK ALERT (10:00 PM)"
            message = f"URGENT: Complete your {platforms_str} problem of the day before midnight!"
            print(f"[+] Sending 10:00 PM Urgent Loud Alarm alert for {platforms_str}...")
            send_ntfy_notification(ntfy_topic, title, message, priority="5", tags="rotating_light,alarm")
    else:
        print("[+] Both LC and GFG daily tasks are checked (1). No reminder needed!")

if __name__ == "__main__":
    main()
