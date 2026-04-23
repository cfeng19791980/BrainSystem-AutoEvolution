@echo off
chcp 65001 > nul
echo ========================================
echo Brain System V3.0 - 安全启动脚本
echo ========================================
echo.

:: [优化] 强制清理5002端口所有旧进程
echo [INFO] 清理旧进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5002" ^| findstr "LISTENING"') do (
    echo [INFO] 杀死进程 PID: %%a
    taskkill /PID %%a /F > nul 2>&1
)

:: 等待进程完全退出
timeout /t 3 /nobreak > nul

:: 确认端口已释放
echo.
echo [INFO] 确认端口状态...
netstat -ano | findstr ":5002" > nul
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] 端口5002仍被占用，强制清理所有Python进程
    taskkill /IM python.exe /F > nul 2>&1
    timeout /t 2 /nobreak > nul
)

:: 启动Brain Entry
cd /d "C:\Users\Administrator\.openclaw\brain-system\core"
echo.
echo [INFO] 启动 Brain Entry API...
start "Brain Entry V3.0" /MIN python brain_entry.py

:: 等待启动完成
timeout /t 5 /nobreak > nul

:: 检查服务状态
echo.
echo [INFO] 检查服务状态...
netstat -ano | findstr ":5002" | findstr "LISTENING"
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Brain Entry 已启动
    echo [INFO] 端口5002监听正常
) else (
    echo [ERROR] Brain Entry 启动失败
    echo [INFO] 请检查日志: .openclaw\logs\brain_entry.log
)

echo.
echo ========================================
echo Brain System 启动完成
echo ========================================
pause