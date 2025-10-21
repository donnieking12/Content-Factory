@echo off
REM EC2 Management Script for Content Factory

SET EC2_HOST=ec2-13-36-168-66.eu-west-3.compute.amazonaws.com
SET SSH_KEY=C:\Users\HP\Desktop\Donnie\aws-factory-key.pem

:menu
cls
echo ========================================
echo   Content Factory - EC2 Manager
echo ========================================
echo.
echo   1. Deploy to EC2
echo   2. Connect via SSH
echo   3. Check Application Status
echo   4. View Application Logs
echo   5. Restart Application
echo   6. Update Application
echo   7. Run Health Check
echo   8. Test YouTube OAuth
echo   9. Exit
echo.
echo ========================================
echo.

set /p choice="Select option (1-9): "

if "%choice%"=="1" goto deploy
if "%choice%"=="2" goto connect
if "%choice%"=="3" goto status
if "%choice%"=="4" goto logs
if "%choice%"=="5" goto restart
if "%choice%"=="6" goto update
if "%choice%"=="7" goto health
if "%choice%"=="8" goto oauth
if "%choice%"=="9" goto end

echo Invalid option!
timeout /t 2
goto menu

:deploy
echo.
echo Starting deployment...
call deploy-to-ec2.bat
pause
goto menu

:connect
echo.
echo Connecting to EC2...
ssh -i "%SSH_KEY%" ubuntu@%EC2_HOST%
pause
goto menu

:status
echo.
echo Checking application status...
ssh -i "%SSH_KEY%" ubuntu@%EC2_HOST% "cd ~/content-factory && docker-compose -f docker-compose.prod.yml ps"
echo.
pause
goto menu

:logs
echo.
echo Fetching logs (last 50 lines)...
echo Press Ctrl+C to stop
ssh -i "%SSH_KEY%" ubuntu@%EC2_HOST% "cd ~/content-factory && docker-compose -f docker-compose.prod.yml logs --tail=50 app"
echo.
pause
goto menu

:restart
echo.
echo Restarting application...
ssh -i "%SSH_KEY%" ubuntu@%EC2_HOST% "cd ~/content-factory && docker-compose -f docker-compose.prod.yml restart"
echo Application restarted!
timeout /t 3
goto menu

:update
echo.
echo Updating application...
ssh -i "%SSH_KEY%" ubuntu@%EC2_HOST% "cd ~/content-factory && git pull origin main && docker-compose -f docker-compose.prod.yml up -d --build"
echo Application updated!
timeout /t 3
goto menu

:health
echo.
echo Running health check...
ssh -i "%SSH_KEY%" ubuntu@%EC2_HOST% "curl -s http://localhost:8000/health | python3 -m json.tool"
echo.
pause
goto menu

:oauth
echo.
echo Testing YouTube OAuth...
echo.
echo Opening browser to test YouTube OAuth...
start http://%EC2_HOST%:8000/api/v1/social-media/youtube/auth-status
echo.
echo Check the browser window for OAuth status
pause
goto menu

:end
echo.
echo Goodbye!
timeout /t 1
exit
