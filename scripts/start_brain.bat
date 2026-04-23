@echo off
chcp 65001 > nul
echo ========================================
echo Brain System V3.0 - 启动脚本
echo ========================================
echo.

cd /d "C:\Users\Administrator\.openclaw\brain-system\core"

:: 检查是否已运行
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find "brain_entry" >NUL
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Brain Entry 可能已在运行
    echo 检查端口5002...
    netstat -ano | find ":5002"
    echo.
)

:: 启动Brain Entry
echo [INFO] 启动 Brain Entry API...
start "Brain Entry V3.0" /MIN python brain_entry.py

:: 等待启动
timeout /t 5 /nobreak > nul

:: 检查端口
echo.
echo [INFO] 检查服务状态...
netstat -ano | find ":5002"
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Brain Entry 已启动在端口5002
) else (
    echo [ERROR] Brain Entry 启动失败
)

echo.
echo ========================================
echo Brain System 启动完成
echo ========================================
pause