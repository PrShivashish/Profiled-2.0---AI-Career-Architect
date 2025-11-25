@echo off
echo ==========================================
echo   PROFILED AUTO-UPDATER - STARTED
echo   Date: %date% Time: %time%
echo ==========================================

:: 1. Go to project directory (YOUR EXACT PATH)
cd /d "C:\Users\shiva\Programming Projects\End-To-End-Job-Matching-System-main"

:: 2. Activate Virtual Environment
call Smartcv\Scripts\activate.bat

:: 3. Run Scraper (Appends new jobs to CSV)
echo [1/2] Scraping new jobs...
python scripts/linkedin_scraper.py

:: 4. Run Ingestor (Updates Database)
echo [2/2] Updating Database...
python scripts/ingest_data.py

echo ==========================================
echo   UPDATE COMPLETE
echo ==========================================
:: Pause for 10 seconds so you can see the result, then close
timeout /t 10