# CP Dashboard (Rainmeter)

> **Note**: This is a perfectly vibe coded project, created because I was facing problems remembering contest dates. 🚀

A lightweight, production-quality, zero-maintenance desktop dashboard for Competitive Programming that displays upcoming contests from **Codeforces** and **LeetCode**.

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

### Step 1: Copy the Rainmeter Skin
1. Copy the `rainmeter` folder from this repository into your Rainmeter Skins directory (typically `C:\Users\Dhruv\OneDrive\Documents\Rainmeter\Skins\`).
2. Rename that folder to `CPDashboard`.

### Step 2: Configure Paths
Open `variables.inc` inside your `Skins\CPDashboard\` directory and verify the paths to Python and the script entry point:
```ini
PythonPath=python
FetcherPath=D:\Projects\CPDashboard\fetch\fetch_contests.py
```

### Step 3: Run the Python Fetcher
Run the Python script once in your terminal to generate the initial `contest.json` database:
```bash
python D:\Projects\CPDashboard\fetch\fetch_contests.py
```

### Step 4: Load the Skin
1. Right-click the Rainmeter system tray icon and click **Manage**.
2. Click **Refresh all** in the bottom-left corner.
3. Select `CPDashboard` -> `CPDashboard.ini` and click **Load** in the top-right.

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
