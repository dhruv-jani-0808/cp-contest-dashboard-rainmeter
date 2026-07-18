# CP Dashboard - Development Roadmap

This document outlines the phased development roadmap for the CP Dashboard.

## Phase Plan

### Phase 1: Foundation (Current)
- [x] Create Git repository and folder structure.
- [x] Create `README.md`, `.gitignore`, and `LICENSE`.
- [x] Create documentation (`roadmap.md`, `architecture.md`, `design.md`).
- [x] Build basic Rainmeter skin UI with dummy static data.

### Phase 2: Python Fetcher Foundation
- [ ] Create `fetch_contests.py` script.
- [ ] Read dummy local JSON file.
- [ ] Format and write output to `contest.json`.

### Phase 3: Codeforces Integration
- [ ] Write Codeforces API provider.
- [ ] Fetch live contests and generate updated `contest.json`.

### Phase 4: LeetCode Integration
- [ ] Write LeetCode GraphQL API provider.
- [ ] Merge contest schedules and generate unified `contest.json`.

### Phase 5: Dynamic Rolling Calendar
- [ ] Implement rolling 28-day logic in Rainmeter (via Lua/measures).
- [ ] Dynamically color dates based on contest schedules.

### Phase 6: Dynamic Contest List
- [ ] Implement dynamic lists for the "Next 7 Days" contest details.
- [ ] Handle timezone and time formatting (12-hour AM/PM format).

### Phase 7: Manual Refresh Button
- [ ] Bind Rainmeter refresh icon to run `fetch_contests.py` and reload skin.

### Phase 8: Windows Startup Integration
- [ ] Configure startup task/shortcut to update contests on boot.

### Phase 9: Polish & Release
- [ ] Refactor and style polish.
- [ ] Package into `.rmskin` installer.
- [ ] Create GitHub Release v1.0.

---

## Future Features (Post-v1.0)
- Hover tooltips with contest information
- Clickable dates to open contest page links
- Custom LeetCode streak widgets
- Settings dashboard for UI customization
- Light / custom developer theme presets
