@echo off
chcp 65001 > nul
echo ========================================
echo Brain System V3.0 - 停止脚本
echo ========================================
echo.

:: 查找端口5002的进程
echo [INFO] 查找端口5002的进程...
for /f "tokens=5" %%a in ('netstat -ano ^| find ":5002"') do (
    echo [INFO] 找到进程 PID: %%a
    taskkill /PID %%a /F > nul 2>&1
)

:: 等待进程结束
timeout /t 2 /nobreak > nul

:: 确认停止
netstat -ano | find ":5002" > nul
if %ERRORLEVEL% EQU 1 (
    echo [SUCCESS] Brain Entry 已停止
) else (
    echo [WARNING] 端口5002仍被占用，尝试强制杀死Python...
    taskkill /IM python.exe /F > nul 2>&1
)

echo.
echo ========================================
echo Brain System 已停止
echo ========================================
pause