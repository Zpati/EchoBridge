# 🤝 EchoBridge — Community Bounty & Developer Challenge

> **Calling all VRChat modders, C# / Python developers, and audio engineers!**  
> We solved **Mic → VRChat Chatbox** translation seamlessly. Now, we need the community's help to solve the holy grail: **In-Game Voice Capture & Overlay Translation**.

---

## 🎯 The Grand Challenge: "Hearing Others & Translating to HUD"

Currently, EchoBridge allows **YOU** to speak in your native tongue and display real-time translations above your avatar's head in VRChat via OSC.

**The missing half:** When other players speak in Japanese, Russian, Spanish, or English, how can we capture **their** voice streams and show translated subtitles on our screen or VR HUD?

---

## 🔍 Why It's Hard (The Technical Bottleneck)

VRChat currently does **not** provide an outward OSC or API stream for remote players' incoming voice data.

### Past Attempt: WASAPI Loopback Capture
We previously prototyped capturing game audio via Windows WASAPI Loopback (`src/core/speaker_engine.py`):
- **Problem 1 (Noise Mixing):** Loopback captures *all* desktop sound together — game music, ambient sound effects, Discord notifications, and player voices are mixed into one audio buffer.
- **Problem 2 (No Speaker Isolation):** Traditional STT engines choke when 3 people speak at once in a crowded world, or when club music is blasting.
- **Problem 3 (No Spatial Placement):** There is no native way to place translated text over the *specific* player's head who spoke it.

---

## 💡 Potential Solutions We Want the Community to Explore

Here are the most promising avenues where developers can contribute:

### 1. 🥽 Native VRChat Companion Mod (MelonLoader / BepInEx / VRCX)
* Build a lightweight client mod that intercepts Unity `AudioSource` components attached to remote player avatars.
* Extract isolated voice streams per player and send them over local WebSocket / UDP to EchoBridge.
* **Impact:** 100% clean voice isolation without background music or environment noise!

### 2. 🧠 AI Speaker Diarization & Source Separation
* Experiment with local ML models like `pyannote.audio` or `demucs` to separate speech from background music.
* Pass isolated speech tracks to `faster-whisper`.

### 3. 🖥️ OpenVR / SteamVR In-Game Overlay
* Create a lightweight SteamVR dashboard overlay (using `OpenVR` / `ovrwatch`) that renders translated speech subtitles right in your headset without needing desktop Alt+Tab.

---

## 🛠️ Archived Source Code Available

The original prototype code for WASAPI Loopback capture has been preserved in the repository at:
📂 [`src/core/speaker_engine.py`](src/core/speaker_engine.py)

Feel free to inspect, refactor, benchmark, or completely replace it!

---

## 🚀 How to Submit Your Solution

1. **Fork** this repository: [github.com/Zpati/EchoBridge](https://github.com/Zpati/EchoBridge)
2. Create a branch: `git checkout -b feature/community-incoming-voice`
3. Implement your prototype or companion tool.
4. Open a **Pull Request (PR)** or start a discussion in [GitHub Issues](https://github.com/Zpati/EchoBridge/issues).
5. All accepted contributors will be permanently credited on the main README and in the app's credits! 🌟
