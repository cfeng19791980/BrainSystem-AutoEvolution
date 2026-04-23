@echo off
chcp 65001 > nul
echo ========================================
echo Brain System V3.0 - 状态检查
echo ========================================
echo.

:: 检查端口
echo [INFO] 检查端口5002...
netstat -ano | find ":5002" > nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Brain Entry API 运行中
    echo.
    echo 端口详情:
    netstat -ano | find ":5002"
    echo.
    
    :: 获取进程详情
    for /f "tokens=5" %%a in ('netstat -ano ^| find ":5002" ^| find "LISTENING"') do (
        echo 进程 PID: %%a
        tasklist /FI "PID eq %%a" /V
    )
) else (
    echo [OFFLINE] Brain Entry API 未运行
    echo 使用 start_brain.bat 启动
)

echo.
echo ========================================
echo Brain System 状态检查完成
echo ========================================
pause