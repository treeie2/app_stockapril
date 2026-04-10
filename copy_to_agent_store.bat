@echo off
chcp 65001
echo 🚀 复制文件到 agent_store...

set SOURCE=e:\github\stock-research-backup
set TARGET=e:\github\agent_store

REM 复制关键文件
copy "%SOURCE%\main.py" "%TARGET%\"
copy "%SOURCE%\requirements.txt" "%TARGET%\"
copy "%SOURCE%\Dockerfile" "%TARGET%\"

REM 复制目录
xcopy "%SOURCE%\data" "%TARGET%\data\" /E /I /Y
xcopy "%SOURCE%\templates" "%TARGET%\templates\" /E /I /Y
xcopy "%SOURCE%\static" "%TARGET%\static\" /E /I /Y

echo ✅ 复制完成!
echo.
echo 下一步：
echo   cd %TARGET%
echo   git add .
echo   git commit -m "Deploy Flask app with Firebase support"
echo   git push origin main
pause
