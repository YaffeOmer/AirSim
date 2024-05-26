@echo off
echo Searching for processes using port 5555...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5555') do (
    echo Killing process with PID %%a
    taskkill /PID %%a /F
)
echo Done.