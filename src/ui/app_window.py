"""
Main Application GUI Window
Cyberpunk / AI Dark HUD Theme with CustomTkinter.
Focused solely on Microphone-to-VRChat OSC Neural Translation.
"""

import time
import threading
import ctypes
import customtkinter as ctk

from src.config import ConfigManager
from src.core.osc_client import VRChatOSCClient
from src.core.translator import TranslationEngine, SUPPORTED_LANGUAGES
from src.core.mic_engine import MicEngine
from src.ui.locales import STRINGS
from src.ui.theme import (
    BG_MAIN, BG_CARD, BG_TERMINAL, BORDER_COLOR,
    CYBER_CYAN, NEON_PURPLE, NEON_BLUE,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_CYAN,
    STATUS_ONLINE, STATUS_OFFLINE, STATUS_BUSY,
    FONT_TITLE, FONT_SUBTITLE, FONT_CARD_HEADER, FONT_LABEL,
    FONT_MONO, FONT_SMALL, FONT_BADGE
)


class AppWindow(ctk.CTk):
    def __init__(self, config: ConfigManager):
        super().__init__()
        self.config = config

        # UI Language: "en" or "tr"
        self.current_locale = self.config.get("ui_lang", "en")

        # Configure Main Window
        self.title(self._t("app_title"))
        self.geometry("820x720")
        self.minsize(760, 640)
        self.configure(fg_color=BG_MAIN)
        self.attributes("-topmost", self.config.get("always_on_top", True))

        # Set Window & Taskbar Icon
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(os.path.dirname(current_dir))
        icon_path = os.path.join(root_dir, "assets", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # Core Engines Initialization
        self.osc_client = VRChatOSCClient(
            ip=self.config.get("osc_ip", "127.0.0.1"),
            port=self.config.get("osc_port", 9000)
        )

        # Translator (Mic)
        mic_src = SUPPORTED_LANGUAGES.get(self.config.get("mic_source_lang", "Türkçe (tr)"), "tr")
        mic_tgt = SUPPORTED_LANGUAGES.get(self.config.get("mic_target_lang", "English (en)"), "en")
        self.mic_translator = TranslationEngine(default_source=mic_src, default_target=mic_tgt)

        # Mic Engine
        self.mic_engine = MicEngine(
            osc_client=self.osc_client,
            translator=self.mic_translator,
            pause_threshold=self.config.get("mic_pause_threshold", 1.2),
            energy_threshold=self.config.get("mic_energy_threshold", 250),
            stt_lang=mic_src,
            mic_device_index=self.config.get("mic_device_index", None)
        )

        # Build Interface
        self._build_header()
        self._build_mic_card()
        self._build_quick_osc_bar()
        self._build_footer()

        # Apply current strings
        self._apply_ui_locale()

        # Start Global Hotkey Listener (F4)
        self._start_hotkey_thread()

    def _t(self, key: str) -> str:
        """Helper to get localized string."""
        return STRINGS.get(self.current_locale, STRINGS["en"]).get(key, key)

    # -------------------------------------------------------------
    # UI BUILDERS
    # -------------------------------------------------------------
    def _build_header(self):
        """Top Cyberpunk Header with Status Badges and Language Switcher"""
        header_frame = ctk.CTkFrame(self, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=12)
        header_frame.pack(fill="x", padx=16, pady=(14, 10))

        # Title & Subtitle Left
        left_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_box.pack(side="left", padx=16, pady=10)

        self.title_lbl = ctk.CTkLabel(
            left_box,
            text=self._t("header_title"),
            font=FONT_TITLE,
            text_color=CYBER_CYAN
        )
        self.title_lbl.pack(anchor="w")

        self.subtitle_lbl = ctk.CTkLabel(
            left_box,
            text=self._t("header_subtitle"),
            font=FONT_SUBTITLE,
            text_color=TEXT_SECONDARY
        )
        self.subtitle_lbl.pack(anchor="w")

        # OSC, UI Language & Topmost Config Right
        right_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_box.pack(side="right", padx=16, pady=10)

        # UI Language Switcher (EN / TR)
        lang_ui_frame = ctk.CTkFrame(right_box, fg_color="transparent")
        lang_ui_frame.pack(side="right", padx=(10, 0))

        self.ui_lang_menu = ctk.CTkOptionMenu(
            lang_ui_frame,
            values=["🇺🇸 English", "🇹🇷 Türkçe"],
            command=self._on_ui_lang_change,
            font=FONT_SMALL,
            fg_color=BG_MAIN,
            button_color=BORDER_COLOR,
            width=115,
            height=28
        )
        current_display = "🇹🇷 Türkçe" if self.current_locale == "tr" else "🇺🇸 English"
        self.ui_lang_menu.set(current_display)
        self.ui_lang_menu.pack(side="right")

        # Topmost Checkbox
        self.topmost_var = ctk.BooleanVar(value=self.config.get("always_on_top", True))
        self.topmost_chk = ctk.CTkCheckBox(
            right_box,
            text=self._t("topmost"),
            font=FONT_LABEL,
            variable=self.topmost_var,
            command=self._toggle_topmost,
            fg_color=NEON_BLUE,
            hover_color=CYBER_CYAN
        )
        self.topmost_chk.pack(side="right", padx=10)

        # OSC Badge
        osc_status_lbl = ctk.CTkLabel(
            right_box,
            text=f"🌐 OSC: {self.config.get('osc_ip', '127.0.0.1')}:{self.config.get('osc_port', 9000)}",
            font=FONT_BADGE,
            text_color=STATUS_ONLINE,
            fg_color="#0D281E",
            corner_radius=8,
            padx=10,
            pady=4
        )
        osc_status_lbl.pack(side="right", padx=10)

    def _build_mic_card(self):
        """Unified, prominent card for Microphone-to-VRChat Translation"""
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=16, pady=4)

        card = ctk.CTkFrame(container, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=12)
        card.pack(fill="both", expand=True)

        # Card Header
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(14, 6))

        self.lbl_mic_title = ctk.CTkLabel(top, text=self._t("mic_title"), font=FONT_CARD_HEADER, text_color=NEON_PURPLE)
        self.lbl_mic_title.pack(side="left")

        self.lbl_mic_hotkey = ctk.CTkLabel(top, text=self._t("mic_hotkey"), font=FONT_SMALL, text_color=TEXT_SECONDARY)
        self.lbl_mic_hotkey.pack(side="right")

        # Status & Toggle Row
        status_row = ctk.CTkFrame(card, fg_color="transparent")
        status_row.pack(fill="x", padx=16, pady=4)

        self.lbl_mic_status = ctk.CTkLabel(
            status_row,
            text=self._t("status_off"),
            font=FONT_BADGE,
            text_color=STATUS_OFFLINE,
            fg_color="#2D1215",
            corner_radius=6,
            padx=10,
            pady=3
        )
        self.lbl_mic_status.pack(side="left")

        self.switch_mic_var = ctk.StringVar(value="off")
        self.switch_mic = ctk.CTkSwitch(
            status_row,
            text="",
            variable=self.switch_mic_var,
            onvalue="on",
            offvalue="off",
            progress_color=STATUS_ONLINE,
            command=self._on_mic_toggle
        )
        self.switch_mic.pack(side="right")

        # Language Selection Row
        lang_row = ctk.CTkFrame(card, fg_color="transparent")
        lang_row.pack(fill="x", padx=16, pady=6)

        lang_options = list(SUPPORTED_LANGUAGES.keys())
        default_src = self.config.get("mic_source_lang", "Türkçe (tr)")
        default_tgt = self.config.get("mic_target_lang", "English (en)")

        self.src_dropdown = ctk.CTkOptionMenu(
            lang_row,
            values=lang_options,
            command=lambda v: self._on_lang_change(True, v),
            font=FONT_LABEL,
            fg_color=BG_MAIN,
            button_color=BORDER_COLOR,
            width=220,
            height=32
        )
        self.src_dropdown.set(default_src)
        self.src_dropdown.pack(side="left", padx=(0, 8))

        arrow_lbl = ctk.CTkLabel(lang_row, text="➔", font=FONT_TITLE, text_color=CYBER_CYAN)
        arrow_lbl.pack(side="left", padx=8)

        self.tgt_dropdown = ctk.CTkOptionMenu(
            lang_row,
            values=lang_options,
            command=lambda v: self._on_lang_change(False, v),
            font=FONT_LABEL,
            fg_color=BG_MAIN,
            button_color=BORDER_COLOR,
            width=220,
            height=32
        )
        self.tgt_dropdown.set(default_tgt)
        self.tgt_dropdown.pack(side="left", padx=(8, 0))

        # Device Selection Helper
        self.mic_devices = self._get_unique_input_devices()
        self.mic_device_names = [d["name"] for d in self.mic_devices]

        device_row = ctk.CTkFrame(card, fg_color="transparent")
        device_row.pack(fill="x", padx=16, pady=(4, 6))

        self.lbl_mic_dev = ctk.CTkLabel(device_row, text=self._t("device_select"), font=FONT_LABEL, text_color=TEXT_SECONDARY)
        self.lbl_mic_dev.pack(side="left", padx=(0, 8))

        dev_values = self.mic_device_names if self.mic_device_names else ["Varsayılan Mikrofon (Default)"]
        saved_dev = self.config.get("mic_device_name", dev_values[0])
        if saved_dev not in dev_values:
            saved_dev = dev_values[0]

        self.mic_dev_menu = ctk.CTkOptionMenu(
            device_row,
            values=dev_values,
            command=self._on_mic_device_change,
            font=FONT_LABEL,
            fg_color=BG_MAIN,
            button_color=BORDER_COLOR,
            height=30
        )
        self.mic_dev_menu.set(saved_dev)
        self.mic_dev_menu.pack(side="left", fill="x", expand=True)

        # Silence Slider Row
        slider_row = ctk.CTkFrame(card, fg_color="transparent")
        slider_row.pack(fill="x", padx=16, pady=4)

        self.lbl_mic_pause = ctk.CTkLabel(
            slider_row,
            text=f"{self._t('silence_wait')}: {self.config.get('mic_pause_threshold', 1.2)}s",
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY
        )
        self.lbl_mic_pause.pack(side="left")

        self.slider_mic_pause = ctk.CTkSlider(
            slider_row,
            from_=0.5,
            to=3.0,
            number_of_steps=25,
            command=lambda v: self._on_mic_slider(v),
            progress_color=NEON_PURPLE,
            button_color=CYBER_CYAN
        )
        self.slider_mic_pause.set(self.config.get("mic_pause_threshold", 1.2))
        self.slider_mic_pause.pack(side="right", fill="x", expand=True, padx=(10, 0))

        # Terminal Log Console
        self.txt_mic_logs = ctk.CTkTextbox(
            card,
            font=FONT_MONO,
            fg_color=BG_TERMINAL,
            text_color=TEXT_CYAN,
            border_color=BORDER_COLOR,
            border_width=1,
            corner_radius=8
        )
        self.txt_mic_logs.pack(fill="both", expand=True, padx=16, pady=(8, 14))

    def _get_unique_input_devices(self):
        """Lists distinct microphone input devices."""
        import speech_recognition as sr
        devices = [{"name": "Varsayılan Mikrofon (Default)", "index": None}]
        try:
            names = sr.Microphone.list_microphone_names()
            seen = set()
            for idx, name in enumerate(names):
                clean_name = name.strip()
                if clean_name not in seen and ("Mikrofon" in clean_name or "Microphone" in clean_name or "Input" in clean_name):
                    seen.add(clean_name)
                    devices.append({"name": f"[{idx}] {clean_name}", "index": idx})
        except Exception:
            pass
        return devices

    def _on_mic_device_change(self, selected_name: str):
        self.config.set("mic_device_name", selected_name)
        dev_index = None
        for d in self.mic_devices:
            if d["name"] == selected_name:
                dev_index = d["index"]
                break
        self.config.set("mic_device_index", dev_index)
        self.mic_engine.set_device_index(dev_index)
        self.log_mic(f"🎤 Mikrofon Cihazı Seçildi: {selected_name}")

    def _build_quick_osc_bar(self):
        """Quick Direct Input Bar to test OSC or send manual message without speaking"""
        bar = ctk.CTkFrame(self, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=12)
        bar.pack(fill="x", padx=16, pady=6)

        self.quick_label = ctk.CTkLabel(bar, text=self._t("quick_label"), font=FONT_LABEL, text_color=TEXT_PRIMARY)
        self.quick_label.pack(side="left", padx=(14, 8), pady=8)

        self.quick_input = ctk.CTkEntry(
            bar,
            placeholder_text=self._t("quick_placeholder"),
            font=FONT_LABEL,
            fg_color=BG_TERMINAL,
            border_color=BORDER_COLOR,
            text_color=TEXT_PRIMARY
        )
        self.quick_input.pack(side="left", fill="x", expand=True, padx=6, pady=8)
        self.quick_input.bind("<Return>", lambda e: self._send_quick_message())

        self.quick_send_btn = ctk.CTkButton(
            bar,
            text=self._t("quick_send_btn"),
            font=FONT_LABEL,
            fg_color=NEON_BLUE,
            hover_color=CYBER_CYAN,
            command=self._send_quick_message,
            width=140
        )
        self.quick_send_btn.pack(side="right", padx=(8, 14), pady=8)

    def _build_footer(self):
        """Footer Bar with status notes and Clear Logs button"""
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(2, 10))

        self.info_lbl = ctk.CTkLabel(
            footer,
            text=self._t("tip_info"),
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY
        )
        self.info_lbl.pack(side="left")

        self.clear_btn = ctk.CTkButton(
            footer,
            text=self._t("clear_logs_btn"),
            font=FONT_SMALL,
            fg_color=BG_CARD,
            hover_color=BORDER_COLOR,
            command=self._clear_logs,
            width=110,
            height=26
        )
        self.clear_btn.pack(side="right")

    def _on_ui_lang_change(self, val: str):
        locale_code = "tr" if "Türkçe" in val else "en"
        self.current_locale = locale_code
        self.config.set("ui_lang", locale_code)
        self._apply_ui_locale()

    def _apply_ui_locale(self):
        """Updates all UI text elements instantly without app restart."""
        self.title(self._t("app_title"))
        self.title_lbl.configure(text=self._t("header_title"))
        self.subtitle_lbl.configure(text=self._t("header_subtitle"))
        self.topmost_chk.configure(text=self._t("topmost"))

        self.lbl_mic_title.configure(text=self._t("mic_title"))
        self.lbl_mic_hotkey.configure(text=self._t("mic_hotkey"))
        if hasattr(self, 'lbl_mic_dev'):
            self.lbl_mic_dev.configure(text=self._t("device_select"))
        self.lbl_mic_pause.configure(text=f"{self._t('silence_wait')}: {self.config.get('mic_pause_threshold', 1.2)}s")

        self.quick_label.configure(text=self._t("quick_label"))
        self.quick_send_btn.configure(text=self._t("quick_send_btn"))
        self.quick_input.configure(placeholder_text=self._t("quick_placeholder"))

        self.info_lbl.configure(text=self._t("tip_info"))
        self.clear_btn.configure(text=self._t("clear_logs_btn"))

        if self.switch_mic_var.get() == "on":
            self.lbl_mic_status.configure(text=self._t("status_on"))
        else:
            self.lbl_mic_status.configure(text=self._t("status_off"))

    def _toggle_topmost(self):
        val = self.topmost_var.get()
        self.attributes("-topmost", val)
        self.config.set("always_on_top", val)

    def _on_lang_change(self, is_source: bool, value: str):
        code = SUPPORTED_LANGUAGES.get(value, "en")
        if is_source:
            self.config.set("mic_source_lang", value)
            self.mic_engine.set_stt_language(code)
        else:
            self.config.set("mic_target_lang", value)

        src = SUPPORTED_LANGUAGES.get(self.config.get("mic_source_lang"), "tr")
        tgt = SUPPORTED_LANGUAGES.get(self.config.get("mic_target_lang"), "en")
        self.mic_translator.set_languages(src, tgt)
        msg = self._t("lang_changed_mic").format(src=src, tgt=tgt)
        self.log_mic(msg)

    def _on_mic_slider(self, value):
        rounded = round(float(value), 1)
        self.lbl_mic_pause.configure(text=f"{self._t('silence_wait')}: {rounded}s")
        self.mic_engine.set_pause_threshold(rounded)
        self.config.set("mic_pause_threshold", rounded)

    def _send_quick_message(self):
        text = self.quick_input.get().strip()
        if not text:
            return
        self.quick_input.delete(0, "end")
        self.osc_client.send_chatbox_message(
            text,
            typing_indicator=True,
            log_callback=lambda msg: self.log_mic(f"💬 [Chatbox] {text}")
        )

    def _clear_logs(self):
        self.txt_mic_logs.delete("1.0", "end")

    # -------------------------------------------------------------
    # MICROPHONE CHANNEL LOGIC
    # -------------------------------------------------------------
    def _on_mic_toggle(self):
        if self.switch_mic_var.get() == "on":
            self.lbl_mic_status.configure(text=self._t("status_busy"), text_color=STATUS_BUSY, fg_color="#332205")
            self.switch_mic.configure(state="disabled")
            threading.Thread(target=self._start_mic_worker, daemon=True).start()
        else:
            self.mic_engine.stop_listening()
            self.lbl_mic_status.configure(text=self._t("status_off"), text_color=STATUS_OFFLINE, fg_color="#2D1215")
            self.log_mic(self._t("mic_stopped"))

    def _start_mic_worker(self):
        try:
            self.mic_engine.start_listening(
                on_translation=lambda src, trans: self.after(0, self._on_mic_result, src, trans),
                on_status=lambda st: self.after(0, self.log_mic, st)
            )
            self.after(0, self._ui_mic_started)
        except Exception as e:
            self.after(0, self._ui_mic_failed, str(e))

    def _ui_mic_started(self):
        self.switch_mic.configure(state="normal")
        self.lbl_mic_status.configure(text=self._t("status_on"), text_color=STATUS_ONLINE, fg_color="#0D281E")

    def _ui_mic_failed(self, err: str):
        self.switch_mic.configure(state="normal")
        self.switch_mic_var.set("off")
        self.lbl_mic_status.configure(text=self._t("status_err"), text_color=STATUS_OFFLINE, fg_color="#2D1215")
        self.log_mic(f"🔴 Error: {err}")

    def _on_mic_result(self, src: str, trans: str):
        ts = time.strftime("%H:%M:%S")
        self.log_mic(f"[{ts}] {self._t('you_label')}: {src}")
        self.log_mic(f"[{ts}] {self._t('vrc_label')}: {trans}\n")

    def log_mic(self, msg: str):
        self.txt_mic_logs.insert("end", f"{msg}\n")
        self.txt_mic_logs.see("end")

    # -------------------------------------------------------------
    # GLOBAL HOTKEYS (F4)
    # -------------------------------------------------------------
    def _start_hotkey_thread(self):
        t = threading.Thread(target=self._hotkey_listener_loop, daemon=True, name="HotkeyThread")
        t.start()

    def _hotkey_listener_loop(self):
        """Asynchronous Windows hotkey polling via GetAsyncKeyState (VK_F4=0x73)"""
        VK_F4 = 0x73
        f4_down = False

        while True:
            try:
                is_f4 = bool(ctypes.windll.user32.GetAsyncKeyState(VK_F4) & 0x8000)
                if is_f4 and not f4_down:
                    f4_down = True
                    self.after(0, self._toggle_mic_hotkey)
                elif not is_f4:
                    f4_down = False
            except Exception:
                pass
            time.sleep(0.06)

    def _toggle_mic_hotkey(self):
        current = self.switch_mic_var.get()
        new_val = "off" if current == "on" else "on"
        self.switch_mic_var.set(new_val)
        self._on_mic_toggle()
