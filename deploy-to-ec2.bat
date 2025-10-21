@echo off
REM Content Factory - Deploy to EC2 (Windows)
REM This script deploys your application to AWS EC2

echo ========================================
echo   Content Factory - EC2 Deployment
echo ========================================
echo.

SET EC2_HOST=ec2-13-36-168-66.eu-west-3.compute.amazonaws.com
SET SSH_KEY=C:\Users\HP\Desktop\Donnie\aws-factory-key.pem
SET PROJECT_DIR=C:\Users\HP\Desktop\Donnie\Content-Factory

echo Step 1: Testing SSH connection...
ssh -i "%SSH_KEY%" ubuntu@%EC2_HOST% "echo 'SSH connection successful!'"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Cannot connect to EC2 instance
    echo Please check:
    echo   1. SSH key permissions
    echo   2. EC2 instance is running
    echo   3. Security group allows SSH from your IP
    pause
    exit /b 1
)

echo.
echo Step 2: Creating remote directory...
ssh -i "%SSH_KEY%" ubuntu@%EC2_HOST% "mkdir -p ~/content-factory"

echo.
echo Step 3: Transferring files to EC2...
echo This may take a few minutes...
scp -i "%SSH_KEY%" -r "%PROJECT_DIR%\*" ubuntu@%EC2_HOST%:~/content-factory/

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: File transfer failed
    pause
    exit /b 1
)

echo.
echo Step 4: Setting up environment on EC2...
ssh -i "%SSH_KEY%" ubuntu@%EC2_HOST% "cd ~/content-factory && chmod +x deploy-ec2.sh && ./deploy-ec2.sh"

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Deployment script failed
    echo Check the logs above for details
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Deployment Complete!
echo ========================================
echo.
echo Your application is now running at:
echo   http://%EC2_HOST%:8000
echo.
echo API Documentation:
echo   http://%EC2_HOST%:8000/docs
echo.
echo Health Check:
echo   http://%EC2_HOST%:8000/health
echo.
echo YouTube OAuth:
echo   http://%EC2_HOST%:8000/api/v1/social-media/youtube/auth
echo.
echo ========================================
echo.
pause
