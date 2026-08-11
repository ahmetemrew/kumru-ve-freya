@echo off
echo ===================================================
echo Kumru x Freya Sesli Asistan - Kurulum Araci
echo ===================================================
echo.

echo [1/2] Python bagimliliklari yukleniyor (pip install -r requirements.txt)...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [DIKKAT] Gerekli kutuphaneler yuklenirken bir hata olustu.
    echo Genellikle Windows uzerinde "llama-cpp-python" kutuphanesi C++ derleyicisi eksikliginden dolayi hata verir.
    echo Bu sorunu cozmek icin asagidaki komutu manuel olarak terminale yapistirarak calistirin:
    echo pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
    echo ardindan setup.bat dosyasini tekrar calistirin.
    echo.
    pause
    exit /b %errorlevel%
)

echo.
echo [2/2] VNGRS Kumru 2B Modeli Indiriliyor...
echo Bu islem internetinizin hizina gore birkac dakika surebilir (Yaklasik 1.6 GB)
python download_kumru.py

echo.
echo ===================================================
echo Kurulum Basariyla Tamamlandi! 
echo ===================================================
echo Asistani baslatmak icin 'run_voice_agent.bat' dosyasina cift tiklayin.
pause
