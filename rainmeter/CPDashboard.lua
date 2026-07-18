-- CP Dashboard Lua Controller
-- Handles dynamic JSON parsing, week-aligned calendar shifting, and contest list formatting.

function Initialize()
    UpdateSkin()
end

function Update()
    -- No continuous updates on every tick. The skin remains static.
end

function UpdateSkin()
    local currentPath = SKIN:GetVariable('CURRENTPATH')
    local jsonPath = currentPath .. 'contest.json'
    
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
    
    local today_time = os.time()
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
            for _, contest in ipairs(data.contests) do
                local c_date = contest.start_time:sub(1, 10)
                if c_date == cell_iso then
                    table.insert(date_contests, contest)
                end
            end
            
            -- Determine state
            local state = "default"
            if #date_contests == 1 then
                state = date_contests[1].platform
            elseif #date_contests >= 2 then
                local has_cf = false
                local has_lc = false
                for _, contest in ipairs(date_contests) do
                    if contest.platform == "codeforces" then has_cf = true end
                    if contest.platform == "leetcode" then has_lc = true end
                end
                
                if has_cf and has_lc then
                    -- Check if any CF and LC contests collide in time (overlap)
                    local same_time = false
                    for i = 1, #date_contests do
                        for j = i + 1, #date_contests do
                            local c1 = date_contests[i]
                            local c2 = date_contests[j]
                            if c1.platform ~= c2.platform then
                                local start1 = c1.timestamp
                                local end1 = c1.timestamp + c1.duration
                                local start2 = c2.timestamp
                                local end2 = c2.timestamp + c2.duration
                                
                                -- Check interval overlap: max(start1, start2) < min(end1, end2)
                                local max_start = math.max(start1, start2)
                                local min_end = math.min(end1, end2)
                                if max_start < min_end then
                                    same_time = true
                                    break
                                end
                            end
                        end
                        if same_time then break end
                    end
                    state = same_time and "purple" or "yellow"
                elseif has_cf then
                    state = "cf"
                else
                    state = "lc"
                end
            end
            
            -- Apply cell style
            local is_today = (cell_iso == today_iso)
            local fillColor = SKIN:GetVariable('ColorCellDefault')
            local textColor = SKIN:GetVariable('ColorTextSecondary')
            
            if state == "codeforces" or state == "cf" then
                fillColor = SKIN:GetVariable('ColorCF')
                textColor = "13,17,23"
            elseif state == "leetcode" or state == "lc" then
                fillColor = SKIN:GetVariable('ColorLC')
                textColor = "13,17,23"
            elseif state == "yellow" then
                fillColor = SKIN:GetVariable('ColorYellow')
                textColor = "13,17,23"
            elseif state == "purple" then
                fillColor = SKIN:GetVariable('ColorPurple')
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
    local today_midnight_time = os.time({
        year = today_date.year,
        month = today_date.month,
        day = today_date.day,
        hour = 0, min = 0, sec = 0
    })
    local seven_days_later_time = today_midnight_time + (8 * 24 * 3600) - 1
    
    -- Filter contests in next 7 days
    local next_7_days_contests = {}
    for _, contest in ipairs(data.contests) do
        if contest.timestamp >= today_midnight_time and contest.timestamp <= seven_days_later_time then
            table.insert(next_7_days_contests, contest)
        end
    end
    
    local num_contests_to_show = #next_7_days_contests
    local no_contests_mode = false
    
    if num_contests_to_show == 0 then
        -- Find nearest upcoming contest
        local nearest = nil
        for _, contest in ipairs(data.contests) do
            if contest.timestamp >= today_midnight_time then
                nearest = contest
                break
            end
        end
        no_contests_mode = true
        num_contests_to_show = nearest and 2 or 1
        if nearest then
            next_7_days_contests = {
                { id = "empty", platform = "none", name = "No contests in the next 7 days.", timestamp = 0 },
                nearest
            }
        else
            next_7_days_contests = {
                { id = "empty", platform = "none", name = "No contests in the next 7 days.", timestamp = 0 }
            }
        end
    end
    
    -- We support up to 6 meters in INI
    local max_meters = 6
    for i = 1, max_meters do
        local iconMeter = string.format("MeterC%dIcon", i)
        local nameMeter = string.format("MeterC%dName", i)
        local timeMeter = string.format("MeterC%dTime", i)
        
        if i <= num_contests_to_show then
            local contest = next_7_days_contests[i]
            
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
                local iconName = "assets/" .. (contest.platform == "codeforces" and "cf.png" or "lc.png")
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
