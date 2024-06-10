@echo off
setlocal

rem Get the current directory
set current_dir=%cd%

rem Open the first command prompt and run the Python script
start cmd /k "cd /d %current_dir% && python goodchain.py"

rem Open the second command prompt and run the Python script
start cmd /k "cd /d %current_dir% && python goodchain.py"

endlocal
