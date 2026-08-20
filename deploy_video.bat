@echo off
REM ============================================================================
REM deploy_video.bat -- manual local "generate + upload one episode right now"
REM runner. Thin wrapper around scripts\upload_now.py (bypasses GitHub Actions
REM entirely, same core.pipeline.run_episode the daily cron uses).
REM
REM Usage (double-click, or from a terminal in this folder):
REM   deploy_video.bat hp01_betrayal_revenge          -> generate + upload (public)
REM   deploy_video.bat hp01_betrayal_revenge unlisted -> generate + upload (unlisted, for testing)
REM   deploy_video.bat all                            -> all 11 channels, one after another
REM   deploy_video.bat                                -> shows usage + the 11 valid channel names
REM
REM Requires (same as GitHub Actions has via secrets, just local files here):
REM   - .env in this folder with GROQ_API_KEY / PIXABAY_API_KEY / PEXELS_API_KEY
REM     (AGNES_API_KEY optional -- falls back to 100%% stock video without it)
REM   - client_secret_a.json / client_secret_b.json / client_secret_c.json
REM   - token_<channel>.json for every channel you plan to run
REM   - ffmpeg and espeak-ng installed and on PATH
REM   - `pip install -r requirements.txt` already run once in this Python env
REM ============================================================================

setlocal

cd /d "%~dp0"

set CHANNEL=%~1
set MODE=%~2

if "%CHANNEL%"=="" (
    echo Usage:
    echo   deploy_video.bat ^<channel_name^> [unlisted]
    echo   deploy_video.bat all [unlisted]
    echo.
    echo Valid channel names:
    echo   hp01_betrayal_revenge
    echo   hp02_court_drama
    echo   hp03_karma_justice
    echo   hp04_veteran_kindness
    echo   hp06_literary_analysis
    echo   hp07_senior_longevity
    echo   hp08_english_learning
    echo   ch01_ai_asmr
    echo   ch03_hindu_mythology
    echo   ch06_eastern_philosophy
    echo.
    echo ^(hp05_sleep_soundscapes is paused -- see CLAUDE.md^)
    goto :end
)

if not exist ".env" (
    echo WARNING: .env not found in %cd% -- GROQ_API_KEY / PIXABAY_API_KEY /
    echo PEXELS_API_KEY need to already be set as real environment variables,
    echo or this run will fail.
)

where ffmpeg >nul 2>nul
if errorlevel 1 (
    echo ERROR: ffmpeg not found on PATH. Install it first ^(e.g. winget install Gyan.FFmpeg^).
    goto :end
)

where espeak-ng >nul 2>nul
if errorlevel 1 (
    echo WARNING: espeak-ng not found on PATH -- Kokoro TTS needs it. Install
    echo it ^(e.g. from https://github.com/espeak-ng/espeak-ng/releases^) if the
    echo voice generation step fails below.
)

set EXTRA_ARGS=
if /i "%MODE%"=="unlisted" set EXTRA_ARGS=--unlisted

if /i "%CHANNEL%"=="all" (
    echo Generating + uploading ALL 11 channels, one after another...
    python scripts\upload_now.py --all %EXTRA_ARGS%
) else (
    echo Generating + uploading: %CHANNEL% ...
    python scripts\upload_now.py %CHANNEL% %EXTRA_ARGS%
)

:end
echo.
pause
endlocal
