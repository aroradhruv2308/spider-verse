@echo off
REM ============================================================
REM  Spider-Verse resync button
REM  Double-click to publish changes to the live site.
REM   - Job-sheet changes  : always synced.
REM   - Daily Log changes   : only if scripts\doc_id.txt exists AND
REM                           the Daily Log doc is link-shared. Otherwise
REM                           the Daily Log just syncs on the nightly run.
REM ============================================================
cd /d C:\Users\dhruv\spider-verse

echo ============================================
echo   Spider-Verse resync
echo ============================================
echo.

echo [1/2] Daily Log...
if exist "scripts\doc_id.txt" (
    python scripts\daily_sync.py
) else (
    echo   Skipped - the private Daily Log syncs automatically each night.
    echo   (To sync it from this button, share the doc "Anyone with the link"
    echo    and save its id in scripts\doc_id.txt - just ask Claude to set it up.)
)
echo.

echo [2/2] Job-sheet changes...
python scripts\sync_sheets.py
echo.

echo All done. You can close this window.
pause
