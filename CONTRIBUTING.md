# 🤝 Contributing to EchoBridge

Thank you for your interest in contributing! This document outlines **known limitations**, **missing features**, and **areas where the community can help**.

---

## 🚨 Critical Missing Features (High Priority)

### ❌ 1. Others' Speech → Translation (Game Audio → Chatbox Overhead)

> **This is the #1 most requested feature and the hardest to implement.**

**Current state:**
- ✅ YOUR microphone → Translated → Appears in YOUR VRChat chatbox
- ❌ OTHER players speaking → We hear it, but **cannot translate it back into VRChat**

**Why it's hard:**
- VRChat does **not** expose individual player voice streams via OSC or any public API
- WASAPI Loopback captures **all system audio mixed together** — no way to isolate "Player X's voice"
- VRChat does not support injecting text above *other* players' heads from an external app
- Even if we transcribe the mixed game audio, we can only **show it in our own UI overlay**, not in VRChat's world space

**What would be needed:**
- VRChat adding an official OSC/API endpoint for received voice-to-text (requested on [Canny](https://feedback.vrchat.com))
- OR a VRChat mod (e.g. via [VRCX](https://github.com/vrcx-team/VRCX) or a BepInEx plugin) that hooks voice packets
- OR speaker diarization ML model to separate voices from mixed audio

**How you can help:**
- Vote on the VRChat Canny feature request for "OSC voice-to-text output"
- Contribute a speaker diarization module using `pyannote.audio` or `whisperx`
- Build a companion VRChat mod (Unity/C#) that relays voice data via local socket

---

### ❌ 2. Offline / Local Translation (No Internet Required)

**Current state:** 100% dependent on Google Translate API + MyMemory (internet required)

**What would be needed:**
- Integrate [LibreTranslate](https://libretranslate.com/) (self-hosted, open source)
- OR use [Argos Translate](https://github.com/argosopentech/argos-translate) (offline Python library)
- OR integrate local Whisper + local NLLB-200 model for full offline pipeline

**How you can help:**
- Add `argostranslate` as an optional offline backend in `src/core/translator.py`
- Add a "Offline Mode" toggle in the UI settings panel

---

### ❌ 3. Whisper AI Integration (Better STT Accuracy)

**Current state:** Uses Google Speech Recognition (cloud, rate-limited, English-biased)

**What would be needed:**
- Integrate [OpenAI Whisper](https://github.com/openai/whisper) or [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- Whisper is dramatically more accurate, supports 99 languages natively, and runs locally
- Currently excluded from EXE build because torch adds ~2GB to package size

**How you can help:**
- Create a separate `whisper_engine.py` that the user can enable if they have GPU/enough RAM
- Build a separate "Whisper Edition" EXE with torch bundled
- Add a STT backend selector in Settings: `Google Cloud | Whisper Small | Whisper Medium`

---

### ❌ 4. Auto Language Detection for Others

**Current state:** User must manually select "source language" of the other person

**What would be needed:**
- Auto-detect the incoming language before translating
- Google Translate does have auto-detect, but it adds ~300ms latency
- For game audio channel especially, we don't know who is speaking or in what language

**How you can help:**
- Add `langdetect` or `lingua` library for fast local language identification
- Add a "Auto-detect" option in the language dropdowns

---

### ❌ 5. VRChat World / Avatar Awareness

**Current state:** App has no idea which VRChat world you're in or who's nearby

**What would be needed:**
- VRCX integration for world/player data
- Auto-switching translation pairs based on world (e.g. Japanese world → auto TR↔JA)
- Player allowlist (only translate speech from friends)

---

### ❌ 6. Text-to-Speech Output (Hear the Translation)

**Current state:** Translations are shown in UI text only

**What would be needed:**
- Use Windows SAPI / Azure TTS / Google TTS to **speak the translation aloud** in your headset
- So you can actually *hear* what the other person said in your language, hands-free in VR

**How you can help:**
- Add `pyttsx3` or `edge-tts` TTS module
- Add volume/voice/speed controls in UI

---

### ❌ 7. Translation History & Export

**Current state:** Log clears on app restart, no export

**What would be needed:**
- SQLite or JSON log of all translations with timestamps
- Export to `.txt` or `.csv`
- In-app history viewer

---

### ❌ 8. macOS / Linux Support

**Current state:** Windows-only (WASAPI Loopback is Windows-specific)

**What would be needed:**
- Replace `pyaudiowpatch` with `sounddevice` + PulseAudio (Linux) or BlackHole (macOS)
- Abstract the audio backend in `speaker_engine.py`

---

## 🟡 Known Bugs / Issues

| Bug | Severity | Notes |
|-----|----------|-------|
| Game audio mixes ALL system sounds (not just VRChat) | Medium | Use RMS threshold slider as workaround |
| Google Translate rate-limit on heavy use | Medium | MyMemory fallback active |
| Game audio → translation lag ~2–4 seconds | Low | Inherent to cloud STT pipeline |
| App may crash if no microphone detected | Medium | Add graceful error handling |
| OSC send fails silently if VRChat not running | Low | Add connection status indicator |
| Translation cache not persisted across restarts | Low | Save cache to disk on exit |
| EXE window icon may not refresh (Windows icon cache) | Very Low | Clear icon cache manually |

---

## 💡 Feature Requests (Nice to Have)

- [ ] Hotkey customization (not hardcoded F4/F5)
- [ ] Multiple OSC target ports (multi-instance VRChat)
- [ ] Translation confidence score display
- [ ] "Favorite phrases" quick-send panel
- [ ] Dark/Light theme toggle
- [ ] System tray minimize
- [ ] Auto-start with Windows option
- [ ] Volume-based voice activity detection (replace silence threshold)
- [ ] Per-language STT model selection

---

## 🛠️ How to Contribute

1. Fork this repo: https://github.com/Zpati/EchoBridge
2. Create a feature branch: `git checkout -b feature/whisper-integration`
3. Make your changes in `src/core/` or `src/ui/`
4. Test with VRChat OSC enabled
5. Submit a Pull Request with a clear description

### Code Structure

```
src/core/translator.py    ← Add new translation backends here
src/core/mic_engine.py    ← Modify STT engine here
src/core/speaker_engine.py ← Game audio capture here
src/ui/app_window.py      ← UI changes here
src/ui/locales.py         ← Add new UI language strings here
```

---

## 📣 Community Channels

- GitHub Issues: https://github.com/Zpati/EchoBridge/issues
- Vote for VRChat OSC voice output: https://feedback.vrchat.com

---

> **Most impactful contribution:** If you can implement even a basic version of  
> **"other players' voice → translated text overlay"** using any approach,  
> it would be a game-changer for the entire VRChat multilingual community. 🌍

