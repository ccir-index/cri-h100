@echo off
:: CRI Daily Collection — Multi-Model Archive
:: Run by Windows Task Scheduler every day at 9:00 AM
:: Fetches ALL Vast.ai listings, archives complete response,
:: filters per-model snapshots, and commits to GitHub

cd /d C:\Users\19136\CCIR

:: Create logs directory if it doesn't exist
mkdir logs 2>nul

:: Get today's date for log entry
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set today=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%

:: Log start
echo. >> logs\collect.log
echo ======================================== >> logs\collect.log
echo CRI Collection started: %today% %time% >> logs\collect.log
echo ======================================== >> logs\collect.log

:: Run collection (fetches all models, archives full response)
python pipeline\collect.py >> logs\collect.log 2>&1

:: Check if collection succeeded
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Collection failed with exit code %ERRORLEVEL% >> logs\collect.log
    exit /b %ERRORLEVEL%
)

:: Stage new data files — archive + all model directories
git add data\archive\*.json data\archive\*.meta.json >> logs\collect.log 2>&1
git add data\h100-sxm-us\*.csv data\h100-sxm-us\*.meta.json >> logs\collect.log 2>&1
git add data\a100-sxm-us\*.csv data\a100-sxm-us\*.meta.json >> logs\collect.log 2>&1
git add data\a100-pcie-us\*.csv data\a100-pcie-us\*.meta.json >> logs\collect.log 2>&1
git add data\h200-sxm-us\*.csv data\h200-sxm-us\*.meta.json >> logs\collect.log 2>&1
git add data\h100-pcie-us\*.csv data\h100-pcie-us\*.meta.json >> logs\collect.log 2>&1
git add data\v100-us\*.csv data\v100-us\*.meta.json >> logs\collect.log 2>&1
git add data\l40s-us\*.csv data\l40s-us\*.meta.json >> logs\collect.log 2>&1

:: Check if there is anything to commit
git diff --cached --quiet
if %ERRORLEVEL% EQU 0 (
    echo No new data to commit. >> logs\collect.log
    exit /b 0
)

:: Commit with today's date
git commit -m "[collect] %today% -- daily snapshot (all models)" >> logs\collect.log 2>&1

:: Push to GitHub
git push >> logs\collect.log 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git push failed. >> logs\collect.log
    exit /b %ERRORLEVEL%
)

echo Collection complete: %today% >> logs\collect.log
