@echo off
REM ============================================================
REM  Spider-Verse resync button
REM  Double-click to publish Daily Log edits + job-sheet changes
REM  to the live site. (New standalone topic Docs still need the
REM  nightly run / Claude — see CLAUDE notes.)
REM ============================================================
cd /d C:\Users\dhruv\spider-verse

echo ============================================
echo   Spider-Verse resync
echo ============================================
echo.

echo [1/2] Publishing Daily Log changes...
python scripts\daily_sync.py
echo.

echo [2/2] Publishing job-sheet changes...
python scripts\sync_sheets.py
echo.

echo All done. You can close this window.
pause
