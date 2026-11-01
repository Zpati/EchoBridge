# 🌐 EchoBridge — Adım Adım Kurulum ve Kullanım Rehberi

Bu rehber, EchoBridge uygulamasının sizin veya başka bir kullanıcının bilgisayarında sıfırdan sorunsuz şekilde nasıl çalıştırılacağını anlatır.

---

## 💻 Bu Program Herkesin Bilgisayarında Çalışır mı?

**Evet! Kesinlikle ve en pratik şekilde çalışır.**

Artık projenin içinde derlenmiş hazır bir `.exe` bulunmaktadır:
* ZIP'i çıkardıktan sonra doğrudan **`EchoBridge.exe`** dosyasına çift tıklamanız yeterlidir.
* Karşı taraftaki kişinin bilgisayarında **Python, terminal, kod veya bat dosyasıyla hiçbir işi yoktur.**
* Doğrudan çalışır ve sağ üstteki menüden arayüz dilini anında **English** veya **Türkçe** yapabilirsiniz.

---

## 📥 0. Adım: İndirme

1. [Releases sayfasına](https://github.com/Zpati/EchoBridge/releases) gidin
2. **`EchoBridge_v2.5.zip`** dosyasını indirin
3. ZIP dosyasına sağ tıklayın → **Tümünü Çıkar** → Bir klasör seçin (örn. `Masaüstü\EchoBridge`)

---

## 🛠️ 1. Adım: Bilgisayarda Hazırlık ve Kurulum

### A) Doğrudan EXE Kullanıyorsanız (Önerilen):
Python veya başka bir şey kurmanıza **gerek yoktur**. Direkt `EchoBridge.exe` çalıştırın.

### B) Kaynak Koddan Çalıştırıyorsanız (Geliştirici):
1. [python.org](https://www.python.org/downloads/) adresinden güncel Python sürümünü indirin.
2. ⚠️ **ÖNEMLİ:** Kurulum ekranının altındaki **"Add python.exe to PATH"** kutucuğunu mutlaka işaretleyin!
3. Klasörün içinde boş bir yere `Shift + Sağ Tık` yapıp **"PowerShell Penceresini Buradan Aç"** deyin:
```bash
pip install -r requirements.txt
```
*(Veya doğrudan klasördeki `run.bat` dosyasına çift tıklayabilirsiniz.)*

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

> 💡 **Not:** VRChat varsayılan olarak **9000** portunu dinler. EchoBridge de otomatik olarak bu porta (`127.0.0.1:9000`) bağlıdır, ekstra bir port ayarı yapmanıza gerek yoktur.

---

## 🚀 3. Adım: EchoBridge'i Başlatma ve Kullanma

1. **`EchoBridge.exe`** dosyasına çift tıklayın.
2. Windows SmartScreen uyarısı çıkarsa → **"Daha Fazla Bilgi"** → **"Yine de Çalıştır"** seçin (güvenlidir, açık kaynaklıdır).
3. Karşınıza **Cyberpunk / AI Dark HUD** temalı modern arayüz gelecektir.

### 🎙️ Mikrofon Çevirisi (Siz ➔ VRChat):
* Dil kutularından kaynak dili (örn. **Türkçe**) ve hedef dili (örn. **English**) seçin.
* **Ses Cihazı (Audio Device)** menüsünden kullandığınız kulaklık veya mikrofonu seçin.
* Açma/kapama anahtarını açın veya klavyenizden **`F4`** tuşuna basın.
* Mikrofona konuştuğunuzda:
  1. Sesiniz algılanır ve Türkçesi arayüze yazılır.
  2. Yapay zeka İngilizceye çevirir (Google Translate veya MyMemory yedek hattı ile).
  3. VRChat avatarınızın başının üstündeki sohbet balonunda otomatik olarak çevrilmiş metin görünür!

### 💬 Hızlı OSC Test Barı:
* Arayüzün en altındaki metin kutusuna herhangi bir mesaj yazıp Enter'a basarak VRChat bağlantınızı saniyeler içinde test edebilirsiniz.

---

<div align="center">

EchoBridge ile dil bariyerini kır 🌍  
**[GitHub](https://github.com/Zpati/EchoBridge)** · [English Guide](SETUP_GUIDE_EN.md)

</div>
