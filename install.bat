@echo off
chcp 65001 > nul

echo start install dependencies...
C:\Users\19722\Desktop\Coding\Study\AlgorithmExperiment\experiment3\.venv\Scripts\pip.exe install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple 
echo successful installed!