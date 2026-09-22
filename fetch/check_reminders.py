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
    
    headers = {
        "Title": title,
        "Priority": str(priority),
        "Tags": tags,
        "User-Agent": "CPDashboard-Reminder/2.1"
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

    script_dir = os.path.dirname(os.path.abspath(__file__))
    variables_path = os.path.normpath(os.path.join(script_dir, "../rainmeter/variables.inc"))
    
    # Also check the OneDrive active skins directory if local doesn't exist
    if not os.path.exists(variables_path):
        onedrive_doc = os.path.expanduser('~/OneDrive/Documents/Rainmeter/Skins/CPDashboard/variables.inc')
        if os.path.exists(onedrive_doc):
            variables_path = onedrive_doc
            
    config = load_variables(variables_path)
    
    show_lc = config.get("ShowLC", "1")
    show_gfg = config.get("ShowGFG", "1")
    ntfy_topic = config.get("NtfyTopic", "dhruv_potd_streak")
    
    print(f"[{datetime.now().isoformat()}] Checking POTD streak state for Ntfy.sh (Topic: {ntfy_topic})...")
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
            title = "⚠️ POTD Reminder (8:00 PM)"
            message = f"You haven't completed your {platforms_str} problem of the day today!"
            print(f"[+] Sending 8:00 PM Ntfy alert for {platforms_str}...")
            send_ntfy_notification(ntfy_topic, title, message, priority="3", tags="warning,memo")
        elif args.type == "call":
            title = "🚨 URGENT POTD STREAK ALERT (10:00 PM)"
            message = f"URGENT: Complete your {platforms_str} problem of the day before midnight!"
            print(f"[+] Sending 10:00 PM Urgent Loud Alarm alert for {platforms_str}...")
            send_ntfy_notification(ntfy_topic, title, message, priority="5", tags="rotating_light,alarm")
    else:
        print("[+] Both LC and GFG daily tasks are checked (1). No reminder needed!")

if __name__ == "__main__":
    main()
