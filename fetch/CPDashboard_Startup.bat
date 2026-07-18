@echo off
:: CP Dashboard Startup Updater
:: Runs the fetcher once on Windows startup to update contest data.

echo Updating Competitive Programming Dashboard contests...
python "D:\Projects\CPDashboard\fetch\fetch_contests.py"
echo Update complete.
exit
