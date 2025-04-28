@echo off
chcp 65001 > nul

echo start install dependencies...
.venv\Scripts\pip.exe install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple 
echo successful installed!