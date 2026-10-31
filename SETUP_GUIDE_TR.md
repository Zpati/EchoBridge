# 🎮 VRChat AI Translator Pro — Adım Adım Kurulum ve Kullanım Rehberi

Bu rehber, uygulamanın sizin veya başka bir kullanıcının bilgisayarında sıfırdan sorunsuz şekilde nasıl çalıştırılacağını anlatır.

---

## 💻 Bu Program Herkesin Bilgisayarında Çalışır mı?

**Evet! Kesinlikle ve en pratik şekilde çalışır.**

Artık projenin içinde derlenmiş hazır bir `.exe` bulunmaktadır:
* `dist\VRChat_AI_Translator_Pro\VRChat_AI_Translator_Pro.exe` dosyasına çift tıklamanız yeterlidir.
* Karşı taraftaki kişinin bilgisayarında **Python, terminal, kod veya bat dosyasıyla hiçbir işi yoktur.**
* Doğrudan çalışır ve sağ üstteki menüden arayüz dilini anında **English** veya **Türkçe** yapabilirsiniz.

---

## 🛠️ 1. Adım: Bilgisayarda Hazırlık ve Kurulum

### A) Python Kurulu Değilse:
1. [python.org](https://www.python.org/downloads/) adresinden güncel Python sürümünü indirin.
2. ⚠️ **ÖNEMLİ:** Kurulum ekranının altındaki **"Add python.exe to PATH"** kutucuğunu mutlaka işaretleyin!

### B) Bağımlılıkların Yüklenmesi:
Klasörün içinde boş bir yere `Shift + Sağ Tık` yapıp **"PowerShell Penceresini Buradan Aç"** (veya Terminal) deyin ve şu komutu yazın:
```bash
pip install -r requirements.txt
```
*(Veya doğrudan klasördeki `run.bat` dosyasına çift tıklayabilirsiniz, eksik varsa otomatik uyaracaktır.)*

---

## 🥽 2. Adım: VRChat İçi OSC Ayarını Açma (ÇOK ÖNEMLİ!)

VRChat'te chatbox balonuna yazı gönderebilmek için oyun içinden **OSC** özelliğinin açık olması şarttır. Varsayılan olarak kapalıdır!

### Nasıl Açılır?
1. VRChat'e girin (Masaüstü modunda veya VR modunda).
2. **Action Menüsü**'nü açın:
   * **Masaüstü (Klavye):** Klavyedeki **`R`** tuşuna basılı tutun.
   * **VR Modu:** Kontrolcünüzdeki menü tuşuna basarak hızlı aksiyon çarkını açın.
3. Çark menüden sırasıyla:
   * **`Options`** (Ayarlar) seçeneğine tıklayın.
   * **`OSC`** seçeneğine tıklayın.
   * **`Enabled`** (Etkin) butonuna basarak **AÇIK** konuma getirin.
4. Artık VRChat, bilgisayarınızdan gönderilen çeviri mesajlarını kabul etmeye hazırdır!

> 💡 **Not:** VRChat varsayılan olarak **9000** portunu dinler. Programımız da otomatik olarak bu porta (`127.0.0.1:9000`) bağlıdır, ekstra bir port ayarı yapmanıza gerek yoktur.

---

## 🚀 3. Adım: Uygulamayı Başlatma ve Kullanma

1. Klasördeki **`run.bat`** dosyasına çift tıklayın (veya terminalden `python main.py`).
2. Karşınıza **Cyberpunk / AI Dark HUD** temalı modern arayüz gelecektir.

### 🎙️ Mikrofon Çevirisi (Siz ➔ VRChat):
* Dil kutularından kaynak dili (örn. **Türkçe**) ve hedef dili (örn. **English**) seçin.
* Açma/kapama anahtarını açın veya klavyenizden **`F4`** tuşuna basın.
* Mikrofona konuştuğunuzda:
  1. Sesiniz algılanır ve Türkçesi yazılır.
  2. Yapay zeka İngilizceye çevirir.
  3. VRChat başınızın üstündeki sohbet balonunda otomatik olarak İngilizce metin görünür!

### 🔊 Oyun Sesi Çevirisi (VRChat ➔ Siz):
* Dil kutularından kaynak dili (örn. **English**) ve hedef dili (örn. **Türkçe**) seçin.
* Açma/kapama anahtarını açın veya klavyenizden **`F5`** tuşuna basın.
* Karşı taraf konuştuğunda sistem sesi yakalar ve arayüzdeki sağ panele Türkçe çevirisini yazar.
* *Detaylı optimizasyon ve gürültü ayarları için `TECHNICAL_LIMITATIONS.md` dosyasını inceleyin.*

### 💬 Hızlı OSC Test Barı:
* Arayüzün en altındaki metin kutusuna herhangi bir mesaj yazıp Enter'a basarak VRChat bağlantınızı saniyeler içinde test edebilirsiniz.

---

## 📦 4. Adım: EXE Haline Getirme (Dağıtım İçin)

Arkadaşlarınıza veya topluluğa Python kurdurmadan programı vermek için:
1. Klasördeki **`build.bat`** dosyasına çift tıklayın.
2. PyInstaller projeyi otomatik olarak `dist\VRChat_AI_Translator_Pro\` klasörüne derleyecektir.
3. O klasörü zipleyip istediğiniz kişiye gönderebilirsiniz!
