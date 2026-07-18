# CP Dashboard - Architecture

This document describes the software architecture and data flow for the CP Dashboard.

## Architecture Diagram

```
+-------------+         +------------------+
| Codeforces  |         |  LeetCode API    |
| API (JSON)  |         | (GraphQL JSON)   |
+------+------+         +--------+---------+
       |                         |
       +------------+------------+
                    |
                    v
          +---------+--------+
          |  Python Fetcher  |
          | (fetch_contests) |
          +---------+--------+
                    |
                    v (writes file)
          +---------+--------+
          |   contest.json   |
          +---------+--------+
                    |
                    v (reads file)
          +---------+--------+
          |  Rainmeter Skin  |
          |  (CPDashboard)   |
          +------------------+
```

## Key Architectural Constraints
1. **No Continuous Background Processing**: The system must NOT poll or sleep in the background. Rainmeter acts purely as a static display that reads a locally stored JSON file (`contest.json`).
2. **Decoupled Data Fetching**: Rainmeter itself never connects to the internet to query contest details. This prevents Rainmeter freezes, reduces resource usage, and separates UI rendering from data extraction.
3. **Execution Triggers**: The Python fetcher is only executed:
   - On Windows startup (once, then exits immediately).
   - When the user manually clicks the Refresh button on the dashboard.

## Components

### 1. Python Fetcher (`fetch/`)
- `fetch_contests.py`: The entry point script. Orchestrates loading providers, fetching, merging schedules, filtering outdated contests, and writing the unified schema to `contest.json`.
- `providers/codeforces.py`: Fetches and processes upcoming Codeforces contests.
- `providers/leetcode.py`: Queries LeetCode's GraphQL API for upcoming contests.
- `utils.py`: Contains common logic, such as date formatting, time conversion, and error logging.

### 2. Output Schema (`contest.json`)
The format represents a list of contests and calendar metadata:
```json
{
  "last_updated": "2026-07-18T20:48:00+05:30",
  "contests": [
    {
      "id": "cf-1234",
      "platform": "codeforces",
      "name": "Codeforces Round 999 (Div. 2)",
      "start_time": "2026-07-19T20:00:00+05:30",
      "duration": 7200
    },
    {
      "id": "lc-biweekly-150",
      "platform": "leetcode",
      "name": "Biweekly Contest 150",
      "start_time": "2026-07-25T20:00:00+05:30",
      "duration": 5400
    }
  ]
}
```

### 3. Rainmeter Skin (`rainmeter/`)
- `CPDashboard.ini`: Defines visual layouts, labels, fonts, and grid cells.
- `variables.inc`: Contains theme variables (colors, fonts, layout settings).
- `contest.json`: Kept in the `rainmeter/` folder so that it is relative to the skin. Rainmeter uses a Lua parser script or WebParser measures to read values.
