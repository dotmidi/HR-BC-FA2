@echo off
setlocal

set CURRENT_DIR=%cd%

mkdir Node1
mkdir Node2

rem copy goodchain folder from current directory to Node1 and Node2
xcopy /E goodchain Node1
xcopy /E goodchain Node2

rem go to Node1/src and run in cmd python goodchain.py
cd Node1\src
start cmd /k python goodchain.py

rem go back to the current directory
cd %CURRENT_DIR%

rem go to Node2/src and run in cmd python goodchain.py
cd Node2\src
start cmd /k python goodchain.py
