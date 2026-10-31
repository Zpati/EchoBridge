# 🧠 VRChat Karşı Taraf Ses Çevirisi - Teknik Analiz & Çözüm Yol Haritası

## 📌 Giriş: "Neden Karşımdaki Konuşunca Çeviri Tetiklenmiyor?"

VRChat'te **kendi sesinizi** mikrofondan alıp İngilizceye çevirerek chatbox balonuna yazdırmak doğrudan ve %99 sorunsuz çalışırken; **karşıdaki oyuncunun sesini hoparlörden yakalayıp Türkçeye çevirmek** oyun motoru ve Windows ses mimarisinden kaynaklanan özel teknik engellere sahiptir.

Bu doküman, bu problemin kök nedenlerini ve projemizde uyguladığımız / yol haritamızdaki mühendislik çözümlerini detaylandırmaktadır.

---

## 🔍 Kök Neden Analizi (Root Causes)

### 1. Master Loopback Karışımı (Mixed Audio Stream)
* **Problem:** `pyaudiowpatch` kütüphanesi Windows'un **WASAPI Loopback** arabirimini kullanır. Bu arabirim, hoparlörden veya kulaklıktan çıkan **tüm sesi** tek bir ham akış olarak yakalar.
* **Sonuç:** VRChat'te oynarken kulaklığınıza sadece diğer oyuncunun sesi değil; **dünya arka plan müziği (BGM), avatar ses efektleri (SFX), ayak sesleri, Discord konuşmaları ve Windows bildirimleri** de aynı anda gelir.
* Ses akışı saf konuşma olmadığı için konuşma tanıma motoru insan sesini diğer seslerden ayıramaz.

### 2. Google Speech Recognition Hassasiyeti (`UnknownValueError`)
* **Problem:** Google STT (`recognize_google`) saf stüdyo/mikrofon sesine odaklanmıştır.
* **Sonuç:** Ses içinde hafif bir müzik ritmi veya arka plan gürültüsü olduğunda Google API `UnknownValueError` (Anlaşılamayan Ses) döner. Eski sürümde bu hata sessizce yutulduğu için kullanıcı hiçbir şey olmamış gibi hissederdi. Pro sürümünde bu durum artık kullanıcıya arayüzde bildirim olarak gösterilmektedir.

### 3. VRChat 3D Mekansal Ses & Düşük Ses Seviyesi (Spatial Audio)
* **Problem:** VRChat'te diğer avatarların sesleri 3D konumlandırılır (Spatialized 3D Audio). Karşıdaki kişi sizden birkaç metre uzaktaysa sesi daha kısık, yankılı veya filtrelenmiş gelir.
* **Sonuç:** Sabit RMS desibel eşiği (`energy_threshold`) dünya müziğinin altında kaldığında ses algılanamaz ya da müzik eşiği aştığında sonsuz kayıt döngüsüne girer.

### 4. Ses Kartı / VR Başlığı Örnekleme Hızı (Sample Rate Mismatch)
* **Problem:** Birçok oyuncu kulaklığı, harici ses kartı ve VR başlığı (Meta Quest Link, Valve Index vb.) 48.000 Hz, 96.000 Hz veya 24/32-bit Float formatında çalışır.
* **Sonuç:** Ham ses doğrudan 16-bit PCM Mono'ya dönüştürülmeden aktarıldığında ses patlaması, cızırtı veya sıfır ses (sessizlik) meydana gelir.

---

## 🛠️ Pro Sürümde Yapılan İyileştirmeler

Yeni mimaride bu problemler şu adımlarla hafifletilmiştir:

1. **Dinamik Ses Eşiği Kaydırıcısı (RMS Threshold Slider):**
   * Arayüzdeki kaydırıcı ile oyunun arka plan müziği seviyesine göre (örn. 350 - 600 RMS) hassas ayar yapabilirsiniz. Müzik 250 RMS ise eşiği 400'e çekerek müziğin çeviriyi tetiklemesi engellenir.
2. **Çok Kanallı Ses Downmix (Mono Dönüştürme):**
   * `audioop.tomono` kullanılarak 2 kanal veya surround sesler dengeli mono kanala indirgenir.
3. **Şeffaf Tanı ve Durum Geri Bildirimi:**
   * Ses algılandığında veya Google STT gürültü sebebiyle çözemediğinde konsola anında sarı uyarı basılır, böylece sistemin çalıştığı ancak gürültü engeline takıldığı açıkça görülür.

---

## 🚀 Kesin ve Kalıcı Çözüm Yol Haritası (Roadmap)

Karşı tarafın sesini %100 stüdyo berraklığında çevirmek için uygulanabilecek ileri düzey adımlar:

1. **Sanal Ses Kablosu İzolasyonu (Virtual Audio Cable - VAC):**
   * Windows ses ayarlarından veya VRChat içinden çıkış aygıtı olarak "CABLE Input" seçilir.
   * Çevirmen doğrudan sadece VRChat çıkışını dinler. Discord veya Spotify müziği araya karışmaz.
2. **AI Tabanlı Ses Ayrıştırma (Silero VAD / WebRTC VAD):**
   * Basit desibel/RMS eşiği yerine yapay zeka tabanlı ses aktivitesi dedektörü (Voice Activity Detection - VAD) entegre edilecek. Böylece arkada müzik çalsa bile sadece insan sesi tespit edildiğinde çeviri başlatılacaktır.
3. **Yerel Whisper AI STT (Faster-Whisper):**
   * Google STT bulut servisi gürültüye dayanıksızdır. Yerel çalışan `faster-whisper-tiny` veya `base` modelleri gürültülü ve müzikli ortamlarda dahi %90+ doğrulukla konuşmayı yazıya dökebilir.

