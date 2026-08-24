-- CP Dashboard Lua Controller
-- Handles dynamic JSON parsing, week-aligned calendar shifting, contest list formatting,
-- time-based contest expiration, scrolling (up to 4 items visible), visual checkbox styling,
-- and dual timezone-based daily resets (midnight for GFG, 5:30 AM for LC & CF).

local scrollOffset = 0

function Initialize()
    scrollOffset = 0
    UpdateSkin()
end

function Update()
    -- No continuous updates on every tick. The skin remains static.
end

function ScrollDown()
    local currentPath = SKIN:GetVariable('CURRENTPATH')
    local jsonPath = currentPath .. 'contest.json'
    local jsonStr = read_file(jsonPath)
    if not jsonStr then return end
    
    local data = parse_json(jsonStr)
    if not data then return end
    
    local active_contests = get_active_contests(data.contests)
    local list_contests = get_list_contests(active_contests)
    
    local total_contests = #list_contests
    local maxOffset = math.max(0, total_contests - 4)
    
    if scrollOffset < maxOffset then
        scrollOffset = scrollOffset + 1
        UpdateSkin()
    end
end

function ScrollUp()
    if scrollOffset > 0 then
        scrollOffset = scrollOffset - 1
        UpdateSkin()
    end
end

function UpdateSkin()
    local currentPath = SKIN:GetVariable('CURRENTPATH')
    local variablesPath = currentPath .. 'variables.inc'
    local jsonPath = currentPath .. 'contest.json'
    
    local today_time = os.time()
    
    -- DUAL DAILY RESET LOGIC
    -- 1. LC Reset: boundary is 5:30 AM (subtract 5.5 hours = 19800 seconds)
    local adjusted_lc_time = today_time - 19800
    local effective_lc = os.date("%Y-%m-%d", adjusted_lc_time)
    local last_reset_lc = SKIN:GetVariable('LastResetDateLC') or ""
    
    -- 2. GFG Reset: boundary is 12:00 AM midnight (no offset needed)
    local effective_gfg = os.date("%Y-%m-%d", today_time)
    local last_reset_gfg = SKIN:GetVariable('LastResetDateGFG') or ""
    
    local needs_write = false
    
    if last_reset_lc ~= effective_lc then
        SKIN:Bang('!WriteKeyValue', 'Variables', 'ShowLC', '0', variablesPath)
        SKIN:Bang('!WriteKeyValue', 'Variables', 'LastResetDateLC', effective_lc, variablesPath)
        needs_write = true
    end
    
    if last_reset_gfg ~= effective_gfg then
        SKIN:Bang('!WriteKeyValue', 'Variables', 'ShowGFG', '0', variablesPath)
        SKIN:Bang('!WriteKeyValue', 'Variables', 'LastResetDateGFG', effective_gfg, variablesPath)
        needs_write = true
    end
    
    if needs_write then
        SKIN:Bang('!Refresh')
        return
    end
    
    local jsonStr = read_file(jsonPath)
    if not jsonStr then
        print("CPDashboard.lua: contest.json not found.")
        return
    end
    
    local data = parse_json(jsonStr)
    if not data then
        print("CPDashboard.lua: Failed to parse contest.json.")
        return
    end
    
    -- Read checkbox states from Rainmeter
    local showLC = tonumber(SKIN:GetVariable('ShowLC')) or 1
    local showGFG = tonumber(SKIN:GetVariable('ShowGFG')) or 1
    
    -- Update visual styles of the checkboxes (purely standalone UI)
    local lcColor = (showLC == 1) and SKIN:GetVariable('ColorLC') or SKIN:GetVariable('ColorCellDefault')
    local gfgColor = (showGFG == 1) and SKIN:GetVariable('ColorGFG') or SKIN:GetVariable('ColorCellDefault')
    
    SKIN:Bang('!SetOption', 'MeterLCBox', 'Shape', string.format("Rectangle 0,0,12,12,2 | Fill Color %s | Stroke Color #ColorBorder# | StrokeWidth 1", lcColor))
    SKIN:Bang('!SetOption', 'MeterGFGBox', 'Shape', string.format("Rectangle 0,0,12,12,2 | Fill Color %s | Stroke Color #ColorBorder# | StrokeWidth 1", gfgColor))
    
    SKIN:Bang('!UpdateMeter', 'MeterLCBox')
    SKIN:Bang('!UpdateMeter', 'MeterGFGBox')

    -- Filter out completed contests
    local active_contests = get_active_contests(data.contests)
    local today_date = os.date("*t", today_time)
    
    -- Calculate Monday of the current week (Sun=1, Mon=2, ..., Sat=7)
    local wday = today_date.wday
    local days_since_monday = (wday == 1) and 6 or (wday - 2)
    local monday_midnight = os.time({
        year = today_date.year,
        month = today_date.month,
        day = today_date.day,
        hour = 0, min = 0, sec = 0
    }) - (days_since_monday * 24 * 3600)

    local today_iso = string.format("%04d-%02d-%02d", today_date.year, today_date.month, today_date.day)
    
    -- 1. POPULATE 28-DAY CALENDAR GRID
    for r = 0, 3 do
        for c = 0, 6 do
            local cell_index = r * 7 + c
            local cell_time = monday_midnight + (cell_index * 24 * 3600)
            local cell_date = os.date("*t", cell_time)
            local cell_iso = string.format("%04d-%02d-%02d", cell_date.year, cell_date.month, cell_date.day)
            
            -- Find contests on this date
            local date_contests = {}
            for _, contest in ipairs(active_contests) do
                local c_date = contest.start_time:sub(1, 10)
                if c_date == cell_iso then
                    table.insert(date_contests, contest)
                end
            end
            
            -- Determine state
            local state = "default"
            if #date_contests >= 1 then
                state = "leetcode"
            end
            
            -- Apply cell style
            local is_today = (cell_iso == today_iso)
            local fillColor = SKIN:GetVariable('ColorCellDefault')
            local textColor = SKIN:GetVariable('ColorTextSecondary')
            
            if state == "leetcode" then
                fillColor = SKIN:GetVariable('ColorLC')
                textColor = "13,17,23"
            end
            
            local strokeColor = "0,0,0,0"
            local strokeWidth = 0
            if is_today then
                strokeColor = SKIN:GetVariable('ColorTodayBorder')
                strokeWidth = 1.5
                if state == "default" then
                    textColor = SKIN:GetVariable('ColorTextPrimary')
                end
            end
            
            local cellMeterName = string.format("Cell%d_%d", r, c)
            local textMeterName = string.format("Cell%d_%dText", r, c)
            
            local shapeOption = string.format("Rectangle 0,0,#CellSize#,#CellSize#,3 | Fill Color %s | Stroke Color %s | StrokeWidth %.1f", fillColor, strokeColor, strokeWidth)
            
            SKIN:Bang('!SetOption', cellMeterName, 'Shape', shapeOption)
            SKIN:Bang('!SetOption', textMeterName, 'FontColor', textColor)
            SKIN:Bang('!SetOption', textMeterName, 'Text', string.format("%d", cell_date.day))
            
            SKIN:Bang('!UpdateMeter', cellMeterName)
            SKIN:Bang('!UpdateMeter', textMeterName)
        end
    end
    
    -- 2. POPULATE CONTEST LIST (NEXT 7 DAYS)
    local list_contests = get_list_contests(active_contests)
    local total_contests = #list_contests
    
    -- Clamp scrollOffset to valid bounds for a 4-item capacity
    local maxOffset = math.max(0, total_contests - 4)
    if scrollOffset > maxOffset then
        scrollOffset = maxOffset
    end
    if scrollOffset < 0 then
        scrollOffset = 0
    end
    
    local num_contests_to_show = math.min(4, total_contests - scrollOffset)
    local empty_mode = (total_contests == 0)
    
    if empty_mode then
        -- Find nearest upcoming active contest
        local nearest = nil
        for _, contest in ipairs(active_contests) do
            if contest.timestamp >= today_midnight_time then
                nearest = contest
                break
            end
        end
        num_contests_to_show = nearest and 2 or 1
        if nearest then
            list_contests = {
                { id = "empty", platform = "none", name = "No contests in the next 7 days.", timestamp = 0 },
                nearest
            }
        else
            list_contests = {
                { id = "empty", platform = "none", name = "No contests in the next 7 days.", timestamp = 0 }
            }
        end
        scrollOffset = 0
    end
    
    -- We support up to 4 visible meters in INI now
    local max_meters = 4
    for i = 1, max_meters do
        local iconMeter = string.format("MeterC%dIcon", i)
        local nameMeter = string.format("MeterC%dName", i)
        local timeMeter = string.format("MeterC%dTime", i)
        
        if i <= num_contests_to_show then
            local contest = list_contests[i + scrollOffset]
            if empty_mode then
                contest = list_contests[i] -- ignore offset in empty/error mode
            end
            
            if contest.id == "empty" then
                -- Display empty state text only (hide icon and time subtitle)
                SKIN:Bang('!HideMeter', iconMeter)
                SKIN:Bang('!HideMeter', timeMeter)
                SKIN:Bang('!SetOption', nameMeter, 'Text', contest.name)
                SKIN:Bang('!SetOption', nameMeter, 'X', "#Padding#") -- Shift left since icon is hidden
            else
                -- Display regular contest
                SKIN:Bang('!ShowMeter', iconMeter)
                SKIN:Bang('!ShowMeter', timeMeter)
                
                -- Set platform icon
                local iconName = "assets/lc.png"
                SKIN:Bang('!SetOption', iconMeter, 'ImageName', iconName)
                
                -- Set text and subtitle
                SKIN:Bang('!SetOption', nameMeter, 'Text', contest.name)
                SKIN:Bang('!SetOption', nameMeter, 'X', "(#Padding# + 20)")
                
                -- Format time in 12-hour format with AM/PM
                local formatted_time = format_contest_time(contest.timestamp)
                SKIN:Bang('!SetOption', timeMeter, 'Text', formatted_time)
            end
            
            SKIN:Bang('!ShowMeter', nameMeter)
            SKIN:Bang('!UpdateMeter', iconMeter)
            SKIN:Bang('!UpdateMeter', nameMeter)
            SKIN:Bang('!UpdateMeter', timeMeter)
        else
            -- Hide extra meters
            SKIN:Bang('!HideMeter', iconMeter)
            SKIN:Bang('!HideMeter', nameMeter)
            SKIN:Bang('!HideMeter', timeMeter)
        end
    end
    
    SKIN:Bang('!Redraw')
end

function get_active_contests(contests)
    local current_time = os.time()
    local active = {}
    for _, contest in ipairs(contests) do
        -- Time-based Expiration: check if current_time <= start_time + duration
        if current_time <= (contest.timestamp + contest.duration) then
            table.insert(active, contest)
        end
    end
    return active
end

function get_list_contests(active_contests)
    local today_time = os.time()
    local today_date = os.date("*t", today_time)
    local today_midnight_time = os.time({
        year = today_date.year,
        month = today_date.month,
        day = today_date.day,
        hour = 0, min = 0, sec = 0
    })
    local seven_days_later_time = today_midnight_time + (8 * 24 * 3600) - 1
    
    local list = {}
    for _, contest in ipairs(active_contests) do
        if contest.timestamp >= today_midnight_time and contest.timestamp <= seven_days_later_time then
            table.insert(list, contest)
        end
    end
    return list
end

function format_contest_time(c_time)
    local date_part = os.date("%A, %d %b", c_time)
    local hour = tonumber(os.date("%I", c_time))
    local min_ampm = os.date("%M %p", c_time)
    return string.format("%s at %d:%s", date_part, hour, min_ampm)
end

function read_file(path)
    local file = io.open(path, "rb")
    if not file then return nil end
    local content = file:read("*all")
    file:close()
    return content
end

function parse_json(json_str)
    local last_updated = json_str:match('"last_updated"%s*:%s*"([^"]+)"')
    local contests_part = json_str:match('"contests"%s*:%s*%[(.-)%]')
    local contests = {}
    if contests_part then
        for block in contests_part:gmatch("%b{}") do
            local id = block:match('"id"%s*:%s*"([^"]+)"')
            local platform = block:match('"platform"%s*:%s*"([^"]+)"')
            local name = block:match('"name"%s*:%s*"([^"]+)"')
            local start_time = block:match('"start_time"%s*:%s*"([^"]+)"')
            local duration_str = block:match('"duration"%s*:%s*(%d+)')
            if platform and name and start_time then
                -- Parse timestamp during load
                local cy, cm, cd, ch, cmin, cs = start_time:match("(%d+)-(%d+)-(%d+)T(%d+):(%d+):(%d+)")
                local timestamp = 0
                if cy then
                    timestamp = os.time({year=cy, month=cm, day=cd, hour=ch, min=cmin, sec=cs})
                end
                
                table.insert(contests, {
                    id = id,
                    platform = platform,
                    name = name,
                    start_time = start_time,
                    duration = tonumber(duration_str) or 0,
                    timestamp = timestamp
                })
            end
        end
    end
    return { last_updated = last_updated, contests = contests }
end
