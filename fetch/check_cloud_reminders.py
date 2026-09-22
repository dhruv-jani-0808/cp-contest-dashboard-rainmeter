"""
CP Dashboard - Cloud POTD Streak Reminder Checker.
Executed by GitHub Actions in the cloud at 8:00 PM and 10:00 PM IST.
Reads state from Ntfy.sh state bucket and dispatches Ntfy alerts if tasks are incomplete.
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta

# Reconfigure stdout for safe console logs
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

STATE_TOPIC = "dhruv_potd_state_bucket"
POLL_URL = f"https://ntfy.sh/{STATE_TOPIC}/json?poll=1"
DEFAULT_TOPIC = "dhruv_potd_streak"

def send_ntfy_notification(topic, title, message, priority="3", tags="warning"):
    if not topic:
        topic = DEFAULT_TOPIC
        
    url = f"https://ntfy.sh/{urllib.parse.quote(topic)}"
    safe_title = title.encode('ascii', 'ignore').decode('ascii')
    
    headers = {
        "Title": safe_title,
        "Priority": str(priority),
        "Tags": tags,
        "User-Agent": "CPDashboard-CloudReminder/2.2"
    }
    
    data = message.encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res = response.read().decode('utf-8')
            print(f"[+] Ntfy.sh Cloud Notification Sent Successfully (Topic: {topic}): {res}")
            return True
    except Exception as e:
        print(f"[-] Error sending Ntfy.sh alert: {e}")
        return False

def fetch_cloud_state():
    req = urllib.request.Request(POLL_URL, headers={"User-Agent": "CPDashboard-CloudChecker/2.2"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_data = response.read().decode('utf-8')
            lines = [l for l in raw_data.strip().split('\n') if l.strip()]
            if lines:
                last_msg = json.loads(lines[-1])
                msg_body = last_msg.get("message", "")
                if msg_body.startswith('{'):
                    return json.loads(msg_body)
            return None
    except Exception as e:
        print(f"[!] Warning: Could not fetch cloud state from Ntfy ({e}). Assuming incomplete state.")
        return None

def main():
    parser = argparse.ArgumentParser(description="Check CP Dashboard POTD streak reminders from Cloud.")
    parser.add_argument("--type", choices=["whatsapp", "call"], default="whatsapp", help="Type of reminder to send.")
    args = parser.parse_args()

    # Calculate current IST date (UTC + 5.5 hours)
    utc_now = datetime.now(timezone.utc)
    ist_now = utc_now + timedelta(hours=5, minutes=30)
    today_ist_date = ist_now.strftime("%Y-%m-%d")
    
    print(f"[{ist_now.isoformat()}] Checking Cloud POTD streak state for IST Date: {today_ist_date}...")
    
    cloud_data = fetch_cloud_state()
    
    show_lc = 0
    show_gfg = 0
    ntfy_topic = DEFAULT_TOPIC
    
    if cloud_data:
        cloud_date = cloud_data.get("date", "")
        ntfy_topic = cloud_data.get("ntfy_topic", DEFAULT_TOPIC)
        
        # If the cloud state was updated TODAY in IST:
        if cloud_date == today_ist_date:
            show_lc = cloud_data.get("show_lc", 0)
            show_gfg = cloud_data.get("show_gfg", 0)
            print(f"    - Found Today's Cloud State: ShowLC={show_lc}, ShowGFG={show_gfg}")
        else:
            print(f"    - Cloud state date ({cloud_date}) is older than today ({today_ist_date}). Assuming 0/0.")
    else:
        print("    - No cloud data found. Assuming 0/0.")
        
    # Check if either task is unticked (0)
    if show_lc == 0 or show_gfg == 0:
        unticked_list = []
        if show_lc == 0:
            unticked_list.append("LeetCode")
        if show_gfg == 0:
            unticked_list.append("GFG")
            
        platforms_str = " and ".join(unticked_list)
        
        if args.type == "whatsapp":
            title = "POTD Streak Reminder (8:00 PM)"
            message = f"You haven't completed your {platforms_str} problem of the day today!"
            print(f"[+] Sending 8:00 PM Cloud Ntfy alert for {platforms_str}...")
            send_ntfy_notification(ntfy_topic, title, message, priority="3", tags="warning,memo")
        elif args.type == "call":
            title = "URGENT POTD STREAK ALERT (10:00 PM)"
            message = f"URGENT: Complete your {platforms_str} problem of the day before midnight!"
            print(f"[+] Sending 10:00 PM Cloud Urgent Loud Alarm alert for {platforms_str}...")
            send_ntfy_notification(ntfy_topic, title, message, priority="5", tags="rotating_light,alarm")
    else:
        print("[+] Both LC and GFG daily tasks are checked (1) in the cloud. No reminder needed!")

if __name__ == "__main__":
    main()
