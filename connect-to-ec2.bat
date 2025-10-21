@echo off
REM Quick SSH connection to EC2 instance

echo Connecting to EC2 instance...
echo.

SET EC2_HOST=ec2-13-36-168-66.eu-west-3.compute.amazonaws.com
SET SSH_KEY=C:\Users\HP\Desktop\Donnie\aws-factory-key.pem

ssh -i "%SSH_KEY%" ubuntu@%EC2_HOST%
