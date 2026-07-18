# CP Contest Calendar (Rainmeter)

> **Note**: This is a perfectly vibe coded project, created because I was facing problems remembering contest dates. 🚀

A lightweight, production-quality, zero-maintenance desktop calendar dashboard for Competitive Programming that displays upcoming contests from **Codeforces** and **LeetCode**.

---

## Key Features
- **Monday-Sunday Aligned Calendar**: A 28-day week-aligned grid showing contest days categorized by platform. Shifts automatically week-by-week on Mondays.
- **Contest Time Collision Checking**: Cell colors reflect scheduling:
  - **Blue**: Codeforces contests only.
  - **Orange**: LeetCode contests only.
  - **Yellow**: Both platforms on the same day (different times).
  - **Purple**: Platform schedules overlap (time collision!).
- **Dynamic Contest List**: Displays detailed contest information occurring within the next 7 days in a clean 12-hour AM/PM format.
- **Zero Maintenance / No Background Processes**: Fetches only once when Windows starts or when you press the refresh button. The skin remains static, consuming zero background CPU/RAM.

---

## Installation & Setup

We have packaged a single-click installer that auto-detects your system configuration:

1.  **Clone or download** this repository to the path: `D:\Projects\CPDashboard\`
2.  Open the folder in Windows Explorer and double-click **`setup.bat`**.

*That's it!* The installer will automatically:
- Find your active Rainmeter skins folder (including OneDrive redirected paths).
- Deploy the files to `Skins\CPDashboard`.
- Auto-resolve your Python executable path and write it to variables.
- Run the python fetcher once to compile the database.
- Refresh Rainmeter and load the skin directly onto your desktop.

---

## Automation (Optional)

### Run on Windows Startup
To fetch and update contest schedules automatically every time you log in to Windows:
1. Press `Win + R`, type `shell:startup`, and press Enter.
2. Right-click and drag `D:\Projects\CPDashboard\fetch\CPDashboard_Startup.bat` to your Windows startup folder, then select **Create shortcuts here**.

---

## Architecture
```
      Internet
         │
         ▼
  Codeforces API
         │
         ▼
   Python Fetcher  ◄─── (Triggered on startup OR manual refresh button click)
         │
         ▼
    contest.json   ◄─── (Local JSON database, also includes dynamic LeetCode generation)
         │
         ▼
   Rainmeter Lua   ◄─── (CPDashboard.lua parses JSON and updates cells)
         │
         ▼
   Rainmeter Skin  ◄─── (Visual presentation & interactive legend/refresh)
```
*Rainmeter never connects directly to the internet to query contest details, preventing UI freezes.*
