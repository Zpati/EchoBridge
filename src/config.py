"""
Configuration Manager for VRChat Translator Pro
Handles persistent settings stored in config.json.
"""

import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger("Config")

DEFAULT_CONFIG: Dict[str, Any] = {
    "osc_ip": "127.0.0.1",
    "osc_port": 9000,
    "hotkey_mic": "F4",
    "hotkey_speaker": "F5",
    "mic_source_lang": "Türkçe (tr)",
    "mic_target_lang": "English (en)",
    "speaker_source_lang": "English (en)",
    "speaker_target_lang": "Türkçe (tr)",
    "mic_pause_threshold": 1.2,
    "mic_energy_threshold": 250,
    "speaker_energy_threshold": 400,
    "speaker_pause_threshold": 1.0,
    "always_on_top": True,
    "play_osc_sound": True,
    "typing_indicator": True
}


class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.settings: Dict[str, Any] = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.settings.update(data)
                logger.info(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                logger.error(f"Failed to load config, using defaults: {e}")
        else:
            self.save()

    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            logger.info("Saved configuration to config.json")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        self.settings[key] = value
        self.save()
