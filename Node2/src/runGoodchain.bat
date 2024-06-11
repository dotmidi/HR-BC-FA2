@echo off
setlocal

rem Get the current directory
set current_dir=%cd%

rem Open the first command prompt and run the Python script with half width
start cmd /k "mode con: cols=80 lines=25 && cd /d %current_dir% && python goodchain.py"

rem Open the second command prompt and run the Python script with half width
start cmd /k "mode con: cols=80 lines=25 && cd /d %current_dir% && python goodchain.py"

endlocal
