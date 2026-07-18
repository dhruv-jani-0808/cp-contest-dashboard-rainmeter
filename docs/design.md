# CP Dashboard - Design System & UI Specs

This document defines the color palette, fonts, layout grid, and style tokens to achieve a clean, developer-focused dark theme (GitHub Dark/VS Code inspired).

## Color System

All colors are specified in hexadecimal format for Rainmeter (represented as `R,G,B,A` or `R,G,B` inside Rainmeter variables).

### Theme Foundations
- **Background**: `#0D1117` (GitHub Dark canvas) -> RGB `13,17,23`
- **Card Background**: `#161B22` (GitHub Dark panel) -> RGB `22,27,34`
- **Border**: `#30363D` -> RGB `48,54,61`
- **Text Primary**: `#C9D1D9` -> RGB `201,209,217`
- **Text Secondary**: `#8B949E` -> RGB `139,148,158`

### Calendar State Colors
Exactly four calendar state colors are defined:
- **Blue** (Codeforces Only): `#58A6FF` -> RGB `88,166,255`
- **Orange** (LeetCode Only): `#F0883E` -> RGB `240,136,62`
- **Yellow** (Both Platforms, different times): `#D29922` -> RGB `210,153,34`
- **Purple** (Both Platforms, same times): `#BC8CFF` -> RGB `188,140,255`
- **Default Cell (No Contests)**: `#21262D` -> RGB `33,38,45`

### Date Highlights
- **Today**: Distinct outline color `#F0F6FC` (RGB `240,246,252`) and slightly brighter background.

## Typography
Windows system fonts are used to ensure zero setup overhead for the user.
- **Header Font**: `Segoe UI` (Semibold for date title, regular for day names)
- **Code Font / Numbers**: `Consolas` or `Segoe UI` (clean monospace look for calendar days and times)

Font Sizes (Rainmeter default is in points):
- **Title (Date Header)**: `14`
- **Day names / Grid headers**: `8`
- **Grid numbers**: `10`
- **Contest details primary**: `9`
- **Contest details secondary**: `8`

## Layout and Dimensions
The dashboard is designed as a single compact vertical widget:
- **Total Width**: `320px`
- **Total Height**: `500px`
- **Padding**: `16px`

### 1. Header Section
- Top-left: Current day (e.g. `Saturday`) and date (e.g. `18 July 2026`).

### 2. Rolling Calendar Section
- 28-day window starting from today.
- Layout: 7 columns (days of the week), 4 rows.
- Grid Cell Size: `34px x 34px`.
- Spacing between cells: `4px`.
- Every cell displays the day number (e.g., `18`, `19`) and uses a background color representing the contest state.

### 3. Contest List Section ("Next 7 Days")
- Header: `Next 7 Days` (Text Primary, bold).
- List items containing:
  - Small platform indicator icon (Codeforces / LeetCode).
  - Contest title text.
  - Date and time in 12-hour AM/PM format (e.g. `8:00 PM`).
- Empty state: `"No contests in the next 7 days."` + Show nearest upcoming contest.

### 4. Refresh Button
- Placed in the bottom-right corner.
- Modern minimalist circular arrow icon.
- Size: `18px x 18px`.
