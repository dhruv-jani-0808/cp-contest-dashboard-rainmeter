"""
LeetCode Contest Provider.
Generates upcoming Weekly and Biweekly contests dynamically based on standard schedules:
- Weekly: Every Sunday at 8:00 AM local time.
- Biweekly: Every alternate Saturday at 8:00 PM local time.
"""

from datetime import date, datetime, timedelta
from fetch import utils

def fetch_upcoming_contests():
    """
    Dynamically generates Weekly and Biweekly LeetCode contests for the 28-day window
    starting from the Monday of the current week.
    Returns:
        list: A list of standardized contest dictionaries.
    """
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    
    upcoming = []
    
    # Anchor dates and numbers
    # Today, Saturday, July 18, 2026: Biweekly Contest 148
    biweekly_anchor = date(2026, 7, 18)
    biweekly_num = 148
    
    # Tomorrow, Sunday, July 19, 2026: Weekly Contest 432
    weekly_anchor = date(2026, 7, 19)
    weekly_num = 432
    
    local_tz = utils.get_local_timezone()
    
    # Generate for the 28-day calendar grid (starting from Monday of current week)
    for i in range(28):
        current_date = monday + timedelta(days=i)
        
        # Saturdays (weekday 5 in Python: Mon=0, ..., Sat=5, Sun=6)
        if current_date.weekday() == 5:
            days_diff = (current_date - biweekly_anchor).days
            weeks_diff = days_diff // 7
            if weeks_diff % 2 == 0:
                contest_num = biweekly_num + (weeks_diff // 2)
                # Biweekly is at 8:00 PM local time (20:00)
                start_dt = datetime(current_date.year, current_date.month, current_date.day, 20, 0, 0)
                start_dt = start_dt.astimezone(local_tz)
                upcoming.append({
                    "id": f"lc-biweekly-{contest_num}",
                    "platform": "leetcode",
                    "name": f"Biweekly Contest {contest_num}",
                    "start_time": start_dt.isoformat(),
                    "duration": 5400
                })
                
        # Sundays (weekday 6)
        elif current_date.weekday() == 6:
            days_diff = (current_date - weekly_anchor).days
            weeks_diff = days_diff // 7
            contest_num = weekly_num + weeks_diff
            # Weekly is at 8:00 AM local time (08:00)
            start_dt = datetime(current_date.year, current_date.month, current_date.day, 8, 0, 0)
            start_dt = start_dt.astimezone(local_tz)
            upcoming.append({
                "id": f"lc-weekly-{contest_num}",
                "platform": "leetcode",
                "name": f"Weekly Contest {contest_num}",
                "start_time": start_dt.isoformat(),
                "duration": 5400
            })
            
    return upcoming
