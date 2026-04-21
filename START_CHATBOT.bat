@echo off
title Quranic Chatbot
echo ========================================
echo   Starting Quranic Chatbot Server...
echo ========================================
echo.
cd /d "C:\Users\Ahsan Computer\Desktop\FYP\Quranic Chat_bot"
echo Starting server... please wait (this takes ~30 seconds to load the AI model)
echo.
echo Once you see "Running on http://127.0.0.1:5000" open your browser and go to:
echo     http://127.0.0.1:5000
echo.
echo To STOP the server, press Ctrl+C
echo.
python app.py
pause
