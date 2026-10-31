# 🚀 VRChat AI Translator Pro — Setup Guide

> **Quick Start for everyone:** No Python, no coding, no setup — just download and run.

---

## 📋 Requirements

- Windows 10 or Windows 11 (64-bit)
- A working microphone
- Internet connection
- VRChat installed and running

---

## 📥 Step 1 — Download

1. Go to the [Releases page](https://github.com/Zpati/VRChat-AI-Translator-Pro/releases)
2. Download `VRChat_AI_Translator_Pro_v2.5.zip`
3. **Right-click** the zip → **Extract All** → Choose a folder (e.g. `Desktop\VRChat Translator`)

---

## 🎮 Step 2 — Enable OSC in VRChat

> [!IMPORTANT]
> This step is required. Without OSC enabled, your translations will NOT appear in your VRChat chatbox.

1. Launch **VRChat**
2. Open the **Main Menu** (click the menu button or press Escape)
3. Go to **Settings**
4. Scroll down to find the **OSC** section
5. Toggle **Enable OSC** → **ON**
6. Confirm the ports are set to:
   - Input: **9000**
   - Output: **9001**
7. Close the settings menu

✅ OSC is now enabled. You only need to do this once.

---

## ▶️ Step 3 — Run the App

1. Open the extracted folder
2. Go into `dist` → `VRChat_AI_Translator_Pro`
3. Double-click **`VRChat_AI_Translator_Pro.exe`**

> [!NOTE]
> Windows may show a SmartScreen warning ("Windows protected your PC").  
> Click **"More info"** → **"Run anyway"** — this is safe, the app is open source.

---

## 🌐 Step 4 — Configure the Translator

Once the app opens:

| Setting | What to do |
|---------|-----------|
| **Your Language** | Select the language YOU speak (e.g. Turkish, Russian, Japanese) |
| **Target Language** | Select the language to translate INTO (usually English) |
| **Microphone** | Select your microphone from the dropdown |
| **Noise Threshold** | Adjust the slider if the app picks up too much background noise |

---

## 🎤 Step 5 — Start Translating

### Mic → VRChat Chatbox (You speaking)
1. Click **"START MIC"** (or press `F4`)
2. Speak into your microphone in your language
3. Your speech will be:
   - Detected automatically
   - Translated to the target language
   - Sent directly to your **VRChat avatar's chatbox**

### Game Audio → UI Overlay (Others speaking)
1. Click **"START GAME AUDIO"** (or press `F5`)
2. The app will listen to your system audio
3. Any speech detected will be transcribed and translated, shown in the **log panel** on screen

> [!WARNING]
> Game Audio mode captures **all** system sounds — not just VRChat voices.  
> Use the **Noise Threshold** slider to filter out music and sound effects.

---

## ⌨️ Hotkeys

| Key | Action |
|-----|--------|
| `F4` | Toggle Mic Translation ON/OFF |
| `F5` | Toggle Game Audio Capture ON/OFF |

These hotkeys work **even when VRChat is focused** — no need to switch windows.

---

## 🌍 Change UI Language

Click the **language button** in the top-right corner of the app to switch between:
- 🇬🇧 **English**
- 🇹🇷 **Türkçe**

---

## ❓ Frequently Asked Questions

**Q: My translation isn't appearing in VRChat chatbox?**  
→ Make sure OSC is enabled in VRChat settings (Step 2). Try restarting VRChat after enabling it.

**Q: The app doesn't detect my microphone?**  
→ Check Windows microphone permissions: Settings → Privacy → Microphone → Allow desktop apps.

**Q: The translation is slow?**  
→ The app uses cloud APIs. A stable internet connection is required. First translation may take 1–2 seconds.

**Q: Windows says the EXE is dangerous?**  
→ This is a false positive from Windows SmartScreen. Click "More info" → "Run anyway". The source code is fully open on GitHub.

**Q: Can the app translate what OTHER players are saying?**  
→ Partially — Game Audio mode captures system audio and translates detected speech, but it mixes all sounds together. Full per-player translation is not currently possible due to VRChat API limitations. See [CONTRIBUTING.md](CONTRIBUTING.md) for the roadmap.

**Q: Does it work in VR (headset)?**  
→ Yes! Run the app on your PC before putting on your headset. Use the hotkeys (F4/F5) to control it without taking off the headset.

---

## 🐛 Found a Bug?

Open an issue on GitHub:  
👉 [https://github.com/Zpati/VRChat-AI-Translator-Pro/issues](https://github.com/Zpati/VRChat-AI-Translator-Pro/issues)

---

## 🔨 Want to Run from Source Code?

```bash
git clone https://github.com/Zpati/VRChat-AI-Translator-Pro.git
cd VRChat-AI-Translator-Pro
pip install -r requirements.txt
python main.py
```

Or double-click `run.bat`.

---

<div align="center">

Made with ❤️ for the VRChat community · [Back to README](README.md)

</div>
