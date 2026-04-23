@echo off
REM 创建Feedback每日聚合定时任务 - 每天00:00执行
REM 执行时间: 晚上12点 (00:00)

echo Creating Feedback Daily Aggregation Task...

schtasks /create /tn "OpenClaw_Feedback_Daily" /tr "python C:\Users\Administrator\.openclaw\brain-system\scripts\feedback_daily_aggregation.py" /sc daily /st 00:00 /rl highest /f

echo.
echo Task created successfully!
echo Task Name: OpenClaw_Feedback_Daily
echo Schedule: Daily at 00:00 (midnight)
echo Script: feedback_daily_aggregation.py
echo.
echo To verify: schtasks /query /tn "OpenClaw_Feedback_Daily"
echo To delete: schtasks /delete /tn "OpenClaw_Feedback_Daily" /f
echo.
pause