"""
Microphone Speech Recognition Engine
Captures user microphone audio, applies speech-to-text (Google STT),
translates via TranslationEngine, and forwards output to VRChat OSC.
"""

import threading
import logging
from typing import Callable, Optional, List, Dict
import speech_recognition as sr
from .osc_client import VRChatOSCClient
from .translator import TranslationEngine

logger = logging.getLogger("MicEngine")


class MicEngine:
    def __init__(
        self,
        osc_client: VRChatOSCClient,
        translator: TranslationEngine,
        pause_threshold: float = 1.2,
        energy_threshold: int = 250,
        mic_device_index: Optional[int] = None,
        stt_lang: str = "tr-TR"
    ):
        self.osc_client = osc_client
        self.translator = translator
        self.pause_threshold = pause_threshold
        self.energy_threshold = energy_threshold
        self.mic_device_index = mic_device_index
        self.stt_lang = stt_lang

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = self.energy_threshold
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = self.pause_threshold

        self.is_listening = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    @staticmethod
    def get_input_devices() -> List[Dict[str, any]]:
        """Returns list of available microphone input devices."""
        devices = []
        try:
            names = sr.Microphone.list_microphone_names()
            for idx, name in enumerate(names):
                devices.append({"index": idx, "name": name})
        except Exception as e:
            logger.error(f"Error enumerating microphones: {e}")
        return devices

    def set_pause_threshold(self, value: float):
        self.pause_threshold = float(value)
        self.recognizer.pause_threshold = self.pause_threshold

    def set_energy_threshold(self, value: int):
        self.energy_threshold = int(value)
        self.recognizer.energy_threshold = self.energy_threshold

    def set_stt_language(self, lang_code: str):
        # Map simple language codes to full STT locales if needed
        locale_map = {
            "tr": "tr-TR",
            "en": "en-US",
            "ja": "ja-JP",
            "ko": "ko-KR",
            "de": "de-DE",
            "fr": "fr-FR",
            "es": "es-ES",
            "ru": "ru-RU",
            "zh-CN": "zh-CN",
            "it": "it-IT",
            "ar": "ar-SA"
        }
        self.stt_lang = locale_map.get(lang_code, lang_code)

    def start_listening(
        self,
        on_translation: Callable[[str, str], None],
        on_status: Optional[Callable[[str], None]] = None,
        send_to_osc: bool = True
    ):
        if self.is_listening:
            return

        self.is_listening = True
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._listen_worker,
            args=(on_translation, on_status, send_to_osc),
            daemon=True,
            name="MicEngineThread"
        )
        self._thread.start()

    def stop_listening(self):
        self.is_listening = False
        self._stop_event.set()

    def _listen_worker(
        self,
        on_translation: Callable[[str, str], None],
        on_status: Optional[Callable[[str], None]],
        send_to_osc: bool
    ):
        try:
            mic = sr.Microphone(device_index=self.mic_device_index)
        except Exception as e:
            if on_status:
                on_status(f"🔴 Mikrofon Başlatılamadı: {e}")
            self.is_listening = False
            return

        with mic as source:
            if on_status:
                on_status("⚙️ Ortam gürültüsü kalibre ediliyor (1 sn)...")
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
            except Exception:
                pass

            if on_status:
                on_status("🟢 Mikrofon dinlemede (Konuştuğunuz an çevrilecek)...")

            while self.is_listening and not self._stop_event.is_set():
                try:
                    # Listen with timeout
                    audio = self.recognizer.listen(source, timeout=1.5, phrase_time_limit=14.0)
                    
                    if not self.is_listening or self._stop_event.is_set():
                        break

                    if on_status:
                        on_status("⚡ Ses algılandı, metne dönüştürülüyor...")

                    # Recognize Google STT
                    text_source = self.recognizer.recognize_google(audio, language=self.stt_lang).strip()
                    if not text_source:
                        continue

                    # Translate
                    text_translated = self.translator.translate(text_source)

                    # Forward to VRChat OSC
                    if send_to_osc and text_translated:
                        self.osc_client.send_chatbox_message(text_translated, typing_indicator=True)

                    # Callback to GUI
                    on_translation(text_source, text_translated)

                    if on_status:
                        on_status("🟢 Dinlemede...")

                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    # Speech was unintelligible
                    continue
                except sr.RequestError as e:
                    if on_status:
                        on_status(f"⚠️ Google STT Bağlantı Hatası: {e}")
                except Exception as e:
                    if self.is_listening and on_status:
                        on_status(f"⚠️ Hata: {e}")

        if on_status:
            on_status("🔴 Mikrofon durduruldu.")
