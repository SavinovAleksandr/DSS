-- AppleScript для автоматической декомпиляции через ILSpy GUI
tell application "ILSpy"
    activate
    delay 2
    
    -- Открыть файл
    tell application "System Events"
        tell process "ILSpy"
            -- File -> Open
            keystroke "o" using command down
            delay 1
            
            -- Ввести путь к файлу
            keystroke "/Users/asavinov/DSS/DynStabSpace.exe"
            delay 1
            key code 36 -- Enter
            delay 3
            
            -- File -> Save Code
            keystroke "s" using {command down, shift down}
            delay 2
            
            -- Ввести путь к выходной папке
            keystroke "/Users/asavinov/DSS/source_code"
            delay 1
            key code 36 -- Enter
            delay 5
        end tell
    end tell
end tell

