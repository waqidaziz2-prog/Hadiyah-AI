@echo off
title Quranic Chatbot - Share via Phone
echo =========================================
echo   Quranic Chatbot - Share via Phone
echo =========================================
echo.
echo This will create a temporary public link that works
echo on ANY phone or device while this window is open.
echo.
cd /d "C:\Users\Ahsan Computer\Desktop\FYP\Quranic Chat_bot"

echo Step 1: Starting chatbot server on port 5000...
start /B python app.py

echo Waiting for server to load (30 seconds)...
timeout /t 30 /nobreak > nul

echo.
echo Step 2: Creating public link via Ngrok...
echo.
echo =====================================================
echo  Your public link will appear below in a moment...
echo  Share this link with ANYONE - works on any phone!
echo  Press Ctrl+C when done to stop sharing.
echo =====================================================
echo.
python -c "from pyngrok import ngrok; import time; tunnel = ngrok.connect(5000); print('\n'); print('========================================'); print('YOUR CHATBOT LINK: ' + tunnel.public_url); print('========================================'); print('\nShare this link on WhatsApp or any app!'); print('Press Ctrl+C to stop.\n'); [time.sleep(1) for _ in iter(int, 1)]"
pause
