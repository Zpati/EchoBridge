"""
Speaker / Loopback Audio Capture Engine
Captures incoming Windows sound (VRChat other players / master audio)
using PyAudioWPatch WASAPI Loopback, processes speech-to-text, and translates to Turkish.
"""

import time
import audioop
import threading
import logging
from typing import Callable, Optional, List, Dict
import speech_recognition as sr
from .translator import TranslationEngine

logger = logging.getLogger("SpeakerEngine")

try:
    import pyaudiowpatch as pyaudio
    HAS_PYAUDIOWPATCH = True
except ImportError:
    try:
        import pyaudio
        HAS_PYAUDIOWPATCH = False
    except ImportError:
        pyaudio = None
        HAS_PYAUDIOWPATCH = False


class SpeakerEngine:
    def __init__(
        self,
        translator: TranslationEngine,
        energy_threshold: int = 400,
        pause_threshold: float = 1.0,
        device_index: Optional[int] = None,
        stt_lang: str = "en-US"
    ):
        self.translator = translator
        self.energy_threshold = energy_threshold
        self.pause_threshold = pause_threshold
        self.device_index = device_index
        self.stt_lang = stt_lang

        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.p: Optional[pyaudio.PyAudio] = None

    @staticmethod
    def get_loopback_devices() -> List[Dict[str, any]]:
        """Returns list of WASAPI loopback output devices available for recording."""
        devices = []
        if not HAS_PYAUDIOWPATCH:
            return devices

        try:
            p = pyaudio.PyAudio()
            try:
                wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            except OSError:
                p.terminate()
                return devices

            for loopback in p.get_loopback_device_info_generator():
                devices.append({
                    "index": loopback["index"],
                    "name": loopback["name"],
                    "channels": loopback["maxInputChannels"],
                    "rate": int(loopback["defaultSampleRate"])
                })
            p.terminate()
        except Exception as e:
            logger.error(f"Error enumerating loopback devices: {e}")
        return devices

    def set_energy_threshold(self, value: int):
        self.energy_threshold = int(value)

    def set_stt_language(self, lang_code: str):
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

    def get_default_device(self, p: pyaudio.PyAudio):
        """Finds default WASAPI loopback device."""
        try:
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
            
            if not default_speakers.get("isLoopbackDevice", False):
                for loopback in p.get_loopback_device_info_generator():
                    if default_speakers["name"] in loopback["name"]:
                        return loopback
            return default_speakers
        except Exception as e:
            logger.error(f"Error obtaining default loopback device: {e}")
            return None

    def start_listening(
        self,
        on_translation: Callable[[str, str], None],
        on_status: Optional[Callable[[str], None]] = None
    ):
        if self.is_listening:
            return

        if not HAS_PYAUDIOWPATCH:
            if on_status:
                on_status("🔴 'pyaudiowpatch' modülü eksik! (pip install pyaudiowpatch)")
            return

        self.is_listening = True
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._listen_worker,
            args=(on_translation, on_status),
            daemon=True,
            name="SpeakerEngineThread"
        )
        self._thread.start()

    def stop_listening(self):
        self.is_listening = False
        self._stop_event.set()

    def _listen_worker(
        self,
        on_translation: Callable[[str, str], None],
        on_status: Optional[Callable[[str], None]]
    ):
        try:
            self.p = pyaudio.PyAudio()
            if self.device_index is not None:
                device_info = self.p.get_device_info_by_index(self.device_index)
            else:
                device_info = self.get_default_device(self.p)

            if not device_info:
                if on_status:
                    on_status("🔴 Hoparlör (WASAPI Loopback) aygıtı bulunamadı.")
                self.is_listening = False
                return

            channels = int(device_info.get("maxInputChannels", 2))
            rate = int(device_info.get("defaultSampleRate", 48000))
            chunk = 1024

            stream = self.p.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=rate,
                input=True,
                frames_per_buffer=chunk,
                input_device_index=device_info["index"]
            )

        except Exception as e:
            if on_status:
                on_status(f"🔴 Ses Akışı Açılamadı: {e}")
            self.is_listening = False
            if self.p:
                try:
                    self.p.terminate()
                except Exception:
                    pass
            return

        dev_name = device_info.get("name", "Bilinmeyen Aygıt")
        if on_status:
            on_status(f"🟢 Oyun sesi dinleniyor: {dev_name[:30]}...")

        chunks_per_sec = rate // chunk
        pause_chunks = int(self.pause_threshold * chunks_per_sec)
        max_chunks = int(12.0 * chunks_per_sec)  # Max 12 seconds per sentence

        frames = []
        silent_chunks = 0
        triggered = False

        try:
            while self.is_listening and not self._stop_event.is_set():
                try:
                    data = stream.read(chunk, exception_on_overflow=False)
                except Exception:
                    continue

                # Downmix to mono if multi-channel for accurate RMS calculation
                if channels > 1:
                    try:
                        mono_data = audioop.tomono(data, 2, 0.5, 0.5)
                    except Exception:
                        mono_data = data
                else:
                    mono_data = data

                rms = audioop.rms(mono_data, 2)

                if rms > self.energy_threshold:
                    if not triggered:
                        triggered = True
                        frames = []
                        silent_chunks = 0
                        if on_status:
                            on_status(f"⚡ Ses algılandı (Gürültü: {rms})...")
                    frames.append(mono_data)
                    silent_chunks = 0
                elif triggered:
                    frames.append(mono_data)
                    silent_chunks += 1

                    # Speech finished (silence detected) or maximum duration reached
                    if silent_chunks >= pause_chunks or len(frames) >= max_chunks:
                        triggered = False
                        raw_audio = b"".join(frames)
                        frames = []
                        silent_chunks = 0

                        # Ignore bursts shorter than 0.6 seconds
                        if len(raw_audio) < (rate * 2 * 0.6):
                            if on_status:
                                on_status("🟢 Dinlemede...")
                            continue

                        if on_status:
                            on_status("🧠 Ses ayrıştırılıyor ve çevriliyor...")

                        try:
                            audio_data = sr.AudioData(raw_audio, rate, 2)
                            text_source = self.recognizer.recognize_google(
                                audio_data,
                                language=self.stt_lang
                            ).strip()

                            if text_source:
                                text_translated = self.translator.translate(text_source)
                                on_translation(text_source, text_translated)
                                if on_status:
                                    on_status("🟢 Dinlemede...")
                        except sr.UnknownValueError:
                            if on_status:
                                on_status("⚠️ Karşı ses anlaşılamadı (Oyun müziği veya gürültü baskın olabilir).")
                        except Exception as e:
                            if on_status:
                                on_status(f"⚠️ Çeviri hatası: {e}")

        finally:
            try:
                stream.stop_stream()
                stream.close()
            except Exception:
                pass
            if self.p:
                try:
                    self.p.terminate()
                except Exception:
                    pass
            if on_status:
                on_status("🔴 Oyun sesi dinleme kapatıldı.")
