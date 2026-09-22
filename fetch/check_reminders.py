"""
CP Dashboard - CallMeBot Daily POTD / Streak Reminder Script.
Checks if ShowLC or ShowGFG checkboxes are unticked (0) in variables.inc,
and sends a WhatsApp message (8:00 PM) or triggers a CallMeBot Voice Call (10:00 PM).
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

def send_whatsapp(phone, text, apikey):
    if not phone or phone == "+91XXXXXXXXXX" or not apikey or apikey == "XXXXXX":
        print("[-] Skipping WhatsApp: UserPhoneNumber or CallMeBotApiKey not configured in variables.inc.")
        return False
        
    encoded_text = urllib.parse.quote(text)
    url = f"https://api.callmebot.com/whatsapp.php?phone={urllib.parse.quote(phone)}&text={encoded_text}&apikey={urllib.parse.quote(apikey)}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            res = response.read().decode('utf-8')
            print(f"[+] WhatsApp Notification Sent Successfully: {res}")
            return True
    except Exception as e:
        print(f"[-] Error sending WhatsApp alert: {e}")
        return False

def trigger_phone_call(phone, text, apikey):
    if not phone or phone == "+91XXXXXXXXXX":
        print("[-] Skipping Phone Call: UserPhoneNumber not configured in variables.inc.")
        return False
        
    encoded_text = urllib.parse.quote(text)
    
    # Primary endpoint for CallMeBot Call API
    url = f"https://api.callmebot.com/start.php?user={urllib.parse.quote(phone)}&text={encoded_text}&lang=en-US"
    
    # Secondary fallback endpoint
    fallback_url = f"https://api.callmebot.com/call.php?phone={urllib.parse.quote(phone)}&text={encoded_text}&apikey={urllib.parse.quote(apikey)}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            res = response.read().decode('utf-8')
            print(f"[+] Phone Call Triggered Successfully: {res}")
            return True
    except Exception as e:
        print(f"[!] Primary call endpoint failed ({e}), trying fallback...")
        try:
            req = urllib.request.Request(fallback_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                res = response.read().decode('utf-8')
                print(f"[+] Fallback Phone Call Triggered Successfully: {res}")
                return True
        except Exception as e2:
            print(f"[-] Error triggering phone call: {e2}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Check CP Dashboard POTD streak reminders.")
    parser.add_argument("--type", choices=["whatsapp", "call"], default="whatsapp", help="Type of reminder to send.")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    variables_path = os.path.normpath(os.path.join(script_dir, "../rainmeter/variables.inc"))
    
    # Also check the OneDrive active skins directory if local doesn't exist
    if not os.path.exists(variables_path):
        appdata = os.environ.get('APPDATA', '')
        onedrive_doc = os.path.expanduser('~/OneDrive/Documents/Rainmeter/Skins/CPDashboard/variables.inc')
        if os.path.exists(onedrive_doc):
            variables_path = onedrive_doc
            
    config = load_variables(variables_path)
    
    show_lc = config.get("ShowLC", "1")
    show_gfg = config.get("ShowGFG", "1")
    phone = config.get("UserPhoneNumber", "")
    apikey = config.get("CallMeBotApiKey", "")
    
    print(f"[{datetime.now().isoformat()}] Checking POTD streak state...")
    print(f"    - ShowLC: {show_lc}, ShowGFG: {show_gfg}")
    
    # Check if either checkbox is unticked (0)
    if show_lc == "0" or show_gfg == "0":
        unticked_list = []
        if show_lc == "0":
            unticked_list.append("LeetCode")
        if show_gfg == "0":
            unticked_list.append("GFG")
            
        platforms_str = " and ".join(unticked_list)
        reminder_text = f"⚠️ POTD Streak Alert! You have not completed your {platforms_str} problem of the day today!"
        
        if args.type == "whatsapp":
            print(f"[+] Sending 8:00 PM WhatsApp reminder for {platforms_str}...")
            send_whatsapp(phone, reminder_text, apikey)
        elif args.type == "call":
            print(f"[+] Triggering 10:00 PM Phone Call TTS voice reminder for {platforms_str}...")
            trigger_phone_call(phone, reminder_text, apikey)
    else:
        print("[+] Both LC and GFG daily tasks are checked (1). No reminder needed!")

if __name__ == "__main__":
    main()
