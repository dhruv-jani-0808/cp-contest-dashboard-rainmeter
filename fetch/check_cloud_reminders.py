"""
CP Dashboard - Cloud POTD Streak Reminder Checker.
Executed ONLY by GitHub Actions in the cloud at 6:00 PM and 8:00 PM IST.
Reads state from Ntfy.sh state bucket (24h history) and dispatches Ntfy alerts if tasks are incomplete.
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
HISTORY_URL = f"https://ntfy.sh/{STATE_TOPIC}/json?since=24h&poll=1"
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
        "User-Agent": "CPDashboard-CloudReminder/2.3"
    }
    
    data = message.encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            response.read()
            print(f"[+] Ntfy.sh Notification Sent (Topic: {topic}, Priority: {priority})")
            return True
    except Exception as e:
        print(f"[-] Error sending Ntfy.sh alert: {e}")
        return False

def fetch_cloud_state(today_ist_date):
    """
    Fetches ALL messages from the last 24 hours from the state bucket,
    then scans backwards to find the LATEST state record matching today's IST date.
    """
    req = urllib.request.Request(HISTORY_URL, headers={"User-Agent": "CPDashboard-CloudChecker/2.3"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_data = response.read().decode('utf-8')
            lines = [l for l in raw_data.strip().split('\n') if l.strip()]
            
            # Scan backwards (newest first) to find latest state for today
            for line in reversed(lines):
                try:
                    msg = json.loads(line)
                    msg_body = msg.get("message", "")
                    if msg_body.startswith('{'):
                        state = json.loads(msg_body)
                        if state.get("date") == today_ist_date:
                            return state
                except (json.JSONDecodeError, KeyError):
                    continue
            
            print(f"    - No state record found for today ({today_ist_date}) in 24h history.")
            return None
    except Exception as e:
        print(f"[!] Warning: Could not fetch cloud state from Ntfy ({e}).")
        return None

def main():
    parser = argparse.ArgumentParser(description="Check CP Dashboard POTD streak reminders from Cloud.")
    parser.add_argument("--type", choices=["whatsapp", "call"], default="whatsapp", help="Type of reminder to send.")
    args = parser.parse_args()

    # Calculate current IST date (UTC + 5.5 hours)
    utc_now = datetime.now(timezone.utc)
    ist_now = utc_now + timedelta(hours=5, minutes=30)
    today_ist_date = ist_now.strftime("%Y-%m-%d")
    
    print(f"[{ist_now.strftime('%Y-%m-%d %H:%M:%S IST')}] Checking Cloud POTD state for: {today_ist_date}")
    
    cloud_data = fetch_cloud_state(today_ist_date)
    
    show_lc = 0
    show_gfg = 0
    ntfy_topic = DEFAULT_TOPIC
    
    if cloud_data:
        show_lc = cloud_data.get("show_lc", 0)
        show_gfg = cloud_data.get("show_gfg", 0)
        ntfy_topic = cloud_data.get("ntfy_topic", DEFAULT_TOPIC)
        print(f"    - Cloud State: ShowLC={show_lc}, ShowGFG={show_gfg}")
    else:
        print("    - No cloud data for today. Assuming both incomplete (0/0).")
        
    # Check if either task is unticked (0)
    if show_lc == 0 or show_gfg == 0:
        unticked_list = []
        if show_lc == 0:
            unticked_list.append("LeetCode")
        if show_gfg == 0:
            unticked_list.append("GFG")
            
        platforms_str = " and ".join(unticked_list)
        
        if args.type == "whatsapp":
            title = "POTD Streak Reminder (6 PM)"
            message = f"You haven't completed your {platforms_str} problem of the day today!"
            print(f"[+] Sending 6:00 PM alert for {platforms_str}...")
            send_ntfy_notification(ntfy_topic, title, message, priority="3", tags="warning,memo")
        elif args.type == "call":
            title = "URGENT POTD STREAK ALERT (8 PM)"
            message = f"URGENT: Complete your {platforms_str} problem of the day before midnight!"
            print(f"[+] Sending 8:00 PM URGENT alarm for {platforms_str}...")
            send_ntfy_notification(ntfy_topic, title, message, priority="5", tags="rotating_light,alarm")
    else:
        print("[+] Both LC and GFG are checked (1). No reminder needed!")

if __name__ == "__main__":
    main()
