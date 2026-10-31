"""
Translation Engine Module
Provides unified interface for text translation using deep-translator with caching and multi-language support.
"""

import logging
from typing import Dict, Optional
from deep_translator import GoogleTranslator

logger = logging.getLogger("Translator")

SUPPORTED_LANGUAGES = {
    "Türkçe (tr)": "tr",
    "English (en)": "en",
    "Japanese / 日本語 (ja)": "ja",
    "Korean / 한국어 (ko)": "ko",
    "German / Deutsch (de)": "de",
    "French / Français (fr)": "fr",
    "Spanish / Español (es)": "es",
    "Russian / Русский (ru)": "ru",
    "Chinese / 中文 (zh-CN)": "zh-CN",
    "Italian / Italiano (it)": "it",
    "Arabic / العربية (ar)": "ar"
}


class TranslationEngine:
    def __init__(self, default_source: str = "tr", default_target: str = "en"):
        self.source = default_source
        self.target = default_target
        self._cache: Dict[str, str] = {}
        self._translator = self._create_translator()

    def set_languages(self, source: str, target: str):
        if source != self.source or target != self.target:
            self.source = source
            self.target = target
            self._cache.clear()
            self._translator = self._create_translator()

    def _create_translator(self):
        try:
            return GoogleTranslator(source=self.source, target=self.target)
        except Exception as e:
            logger.error(f"[Translator Error] Failed to initialize GoogleTranslator: {e}")
            return None

    def translate(self, text: str, source: Optional[str] = None, target: Optional[str] = None) -> str:
        """
        Translates text from source to target language.
        Returns original text if translation fails or if text is empty.
        """
        clean_text = text.strip()
        if not clean_text:
            return ""

        src = source or self.source
        tgt = target or self.target

        # Same language optimization
        if src.lower() == tgt.lower():
            return clean_text

        cache_key = f"{src}->{tgt}:{clean_text}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            if src == self.source and tgt == self.target and self._translator:
                result = self._translator.translate(clean_text)
            else:
                temp_translator = GoogleTranslator(source=src, target=tgt)
                result = temp_translator.translate(clean_text)

            if result:
                self._cache[cache_key] = result
                # Limit cache size
                if len(self._cache) > 200:
                    self._cache.pop(next(iter(self._cache)))
                return result
            return clean_text

        except Exception as e:
            logger.warning(f"[Google Translate Warning] {e}, attempting MyMemory fallback...")
            try:
                from deep_translator import MyMemoryTranslator
                fallback = MyMemoryTranslator(source=src, target=tgt)
                result = fallback.translate(clean_text)
                if result:
                    self._cache[cache_key] = result
                    return result
            except Exception as e2:
                logger.error(f"[Fallback Translation Failed] {e2}")
            return clean_text
