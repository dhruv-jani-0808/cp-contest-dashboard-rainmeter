"""
Codeforces Contest Provider.
"""

import urllib.request
import json
from datetime import date, datetime, timedelta
from fetch import utils

def fetch_upcoming_contests():
    """
    Fetches upcoming contests from the Codeforces API, filtered to fit
    within the 28-day dashboard window starting from Monday of the current week.
    Returns:
        list: A list of standardized contest dictionaries.
    """
    url = "https://codeforces.com/api/contest.list?gym=false"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) CP-Dashboard-Rainmeter'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        if data.get("status") != "OK":
            print("Codeforces API returned non-OK status.")
            return []
            
        # Calculate the 28-day window bounds starting from the Monday of the current week
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        
        # Convert Monday of current week to a timestamp (local midnight)
        monday_midnight = datetime(monday.year, monday.month, monday.day, 0, 0, 0)
        monday_timestamp = int(monday_midnight.timestamp())
        
        # End of the 28-day window
        end_timestamp = monday_timestamp + (28 * 24 * 3600)
        
        upcoming = []
        for contest in data.get("result", []):
            start_seconds = contest.get("startTimeSeconds")
            
            # Filter contests that fall strictly inside the current 28-day calendar grid
            if start_seconds and monday_timestamp <= start_seconds < end_timestamp:
                upcoming.append({
                    "id": f"cf-{contest['id']}",
                    "platform": "codeforces",
                    "name": contest["name"],
                    "start_time": utils.format_unix_time(start_seconds),
                    "duration": contest["durationSeconds"]
                })
        return upcoming
    except Exception as e:
        print(f"Error fetching Codeforces contests: {e}")
        return []
