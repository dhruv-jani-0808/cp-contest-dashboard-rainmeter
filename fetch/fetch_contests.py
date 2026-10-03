"""
CP Dashboard - Contest Fetcher Entry Point.
"""

import sys
import os

# Add parent directory to system path to resolve 'fetch' package imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
from datetime import datetime
from fetch import utils
from fetch.providers import codeforces, leetcode


def main():
    parser = argparse.ArgumentParser(description="Fetch upcoming Competitive Programming contests.")
    parser.add_argument("--mock", action="store_true", help="Generate contest.json using mock data instead of calling APIs.")
    args = parser.parse_args()

    # Determine paths (Save to skin root where CPDashboard.lua reads it)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    output_path = os.path.join(parent_dir, "contest.json")
    dev_rainmeter_path = os.path.normpath(os.path.join(script_dir, "../rainmeter/contest.json"))
    sample_path = os.path.normpath(os.path.join(script_dir, "../tests/sample_contest.json"))

    print("Contest Fetcher Initialized.")

    if args.mock:
        print("Mock mode enabled. Reading mock contest data...")
        mock_data = utils.load_json(sample_path)
        if mock_data:
            # Update last_updated time to current system local time
            local_tz = utils.get_local_timezone()
            mock_data["last_updated"] = datetime.now(local_tz).isoformat()
            if utils.save_json(mock_data, output_path):
                print(f"Mock data successfully written to {output_path}")
                return 0
        else:
            print("Error loading mock contest data from tests/sample_contest.json")
            return 1

    # Live Mode
    print("Skipping Codeforces (disabled)...")
    cf_contests = []

    print("Fetching LeetCode contests...")
    lc_contests = leetcode.fetch_upcoming_contests()
    print(f"Retrieved {len(lc_contests)} upcoming LeetCode contests.")

    # Merge and sort
    all_contests = cf_contests + lc_contests
    
    # Sort contests by their ISO-8601 start_time strings
    all_contests.sort(key=lambda x: x["start_time"])

    # Prepare output data
    local_tz = utils.get_local_timezone()
    output_data = {
        "last_updated": datetime.now(local_tz).isoformat(),
        "contests": all_contests
    }

    if utils.save_json(output_data, output_path):
        print(f"Successfully updated contest database at {output_path}")
        if os.path.exists(os.path.dirname(dev_rainmeter_path)) and os.path.abspath(output_path) != os.path.abspath(dev_rainmeter_path):
            utils.save_json(output_data, dev_rainmeter_path)
        return 0
    else:
        print("Failed to save contest data.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
