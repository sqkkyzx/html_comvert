@echo off
cd /d "%~dp0"
docker build -f Dockerfile -t sqkkyzx/html_convert:latest .
docker push sqkkyzx/html_convert:latest