# Kumru x Freya Sesli Asistan 🇹🇷🎙️

Bu proje, tamamen Türk mühendisliği ürünü olan **VNGRS Kumru 2B** dil modelini ve **FreyaTTS** ses sentezleme motorunu kullanarak tarayıcı üzerinden çalışan uçtan uca bir yerli Sesli Asistan uygulamasıdır. Siri veya ChatGPT'nin sesli modu gibi çalışır, doğrudan cihazınızda çalışarak verilerinizi gizli tutar.

## ✨ Özellikler

- **%100 Yerli Teknoloji:** Dil işleme için `Kumru-2B`, ses için `FreyaTTS`.
- **Gerçek Zamanlı Sohbet:** Tarayıcınızın Web Speech API'sini kullanarak sesinizi anında metne çevirir.
- **Kesintisiz Deneyim (Walkie-Talkie Modu):** Asistan konuşmasını bitirdiğinde mikrofona dokunmanıza gerek kalmadan dinlemeye otomatik olarak devam eder.
- **Bağlam Hafızası:** Son konuştuğunuz 5 diyaloğu hafızasında tutarak akıcı bir sohbet deneyimi sunar.
- **Glassmorphism Arayüz:** Modern, şık ve dinamik bir web arayüzü ile gelir.

## 🚀 Kurulum & Çalıştırma

### 1. Kurulum (Tek Tıkla)
Projeyi klonladıktan veya indirdikten sonra, tüm gereksinimleri kurmak ve **VNGRS Kumru 2B** modelini (yaklaşık 1.6 GB) otomatik olarak indirmek için proje klasöründeki `setup.bat` dosyasına çift tıklamanız yeterlidir.
*(FreyaTTS modeli ise projeyi ilk başlattığınızda otomatik olarak inecektir).*

### 2. Asistanı Başlatın
Kurulumlar tamamlandıktan sonra tek yapmanız gereken başlatma dosyasını çalıştırmaktır:
```bash
run_voice_agent.bat
```
Bu işlem yerel sunucunuzu (`http://127.0.0.1:8001`) başlatacak ve şık arayüzü varsayılan tarayıcınızda otomatik olarak açacaktır. Ekranda yer alan mikrofon ikonuna tıklayıp hemen konuşmaya başlayabilirsiniz!

---

## 🛠️ Teknik Altyapı
- **Backend:** FastAPI, Uvicorn, llama-cpp-python, FreyaTTS
- **Frontend:** HTML5, Vanilla CSS (Glassmorphism), JavaScript (Web Speech API)
- **Modeller:** [VNGRS/Kumru-2B](https://huggingface.co/vngrs-ai/Kumru-2B), [Freya Voice AI](https://huggingface.co/freyavoice/freya-tts)

*Not: FreyaTTS'in orijinal README dosyasına `README_FREYATTS.md` ismiyle ulaşabilirsiniz.*
