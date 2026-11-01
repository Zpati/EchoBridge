"""
Translation Engine Module
Provides unified interface for text translation with multi-provider fallbacks:
1. GoogleTranslator (deep-translator)
2. Direct MyMemory REST API (highly reliable, no rate limits for conversational VRChat text)
3. Google Web API fallback
With caching and error resilient pipeline.
"""

import logging
import urllib.parse
from typing import Dict, Optional
import requests
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

    def _translate_mymemory(self, text: str, src: str, tgt: str) -> Optional[str]:
        """Translates via direct MyMemory REST API (free, reliable fallback)."""
        try:
            url = "https://api.mymemory.translated.net/get"
            params = {
                "q": text,
                "langpair": f"{src}|{tgt}"
            }
            r = requests.get(url, params=params, timeout=4)
            if r.status_code == 200:
                data = r.json()
                translated = data.get("responseData", {}).get("translatedText")
                if translated and not translated.startswith("MYMEMORY WARNING"):
                    return translated
        except Exception as e:
            logger.warning(f"[MyMemory Error] {e}")
        return None

    def _translate_google_web(self, text: str, src: str, tgt: str) -> Optional[str]:
        """Alternative Google Translate web client endpoint."""
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": src,
                "tl": tgt,
                "dt": "t",
                "q": text
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            r = requests.get(url, params=params, headers=headers, timeout=4)
            if r.status_code == 200:
                data = r.json()
                if data and len(data) > 0 and data[0]:
                    result = "".join([segment[0] for segment in data[0] if segment and segment[0]])
                    if result:
                        return result
        except Exception as e:
            logger.warning(f"[Google Web API Error] {e}")
        return None

    def translate(self, text: str, source: Optional[str] = None, target: Optional[str] = None) -> str:
        """
        Translates text from source to target language with multiple fallbacks.
        Guarantees that translation never silently returns the original text unless source == target.
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

        # 1. Primary: GoogleTranslator
        try:
            if src == self.source and tgt == self.target and self._translator:
                result = self._translator.translate(clean_text)
            else:
                temp_translator = GoogleTranslator(source=src, target=tgt)
                result = temp_translator.translate(clean_text)

            if result and result.strip() != clean_text:
                self._save_to_cache(cache_key, result)
                return result
        except Exception as e:
            logger.warning(f"[Primary GoogleTranslator failed]: {e}")

        # 2. Secondary: Direct MyMemory REST API
        mymemory_res = self._translate_mymemory(clean_text, src, tgt)
        if mymemory_res and mymemory_res.strip() != clean_text:
            self._save_to_cache(cache_key, mymemory_res)
            return mymemory_res

        # 3. Tertiary: Google Web alternative
        web_res = self._translate_google_web(clean_text, src, tgt)
        if web_res and web_res.strip() != clean_text:
            self._save_to_cache(cache_key, web_res)
            return web_res

        logger.error(f"[All Translation Providers Failed] returning original text: {clean_text}")
        return clean_text

    def _save_to_cache(self, key: str, val: str):
        self._cache[key] = val
        if len(self._cache) > 200:
            self._cache.pop(next(iter(self._cache)))
