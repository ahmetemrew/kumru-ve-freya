@echo off
cd /d "%~dp0"
echo Akilli Sesli Asistan Baslatiliyor... (Kumru 2B + FreyaTTS)
echo Port 8001 uzerinden calisacaktir. Eger model hala iniyorsa tarayicinizdaki arayuzde hata verebilir, lutfen inmesini bekleyin.
python voice_app.py
pause
