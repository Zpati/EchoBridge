"""
Main Application GUI for VRChat Translator Pro
High-tech AI Cyberpunk HUD interface with dual translation channels,
audio sensitivity calibrators, OSC manual dispatcher, and persistent configuration.
Supports dynamic UI Language switching (English & Türkçe).
"""

import time
import ctypes
import threading
import customtkinter as ctk
from typing import Optional

from .theme import (
    BG_MAIN, BG_CARD, BG_TERMINAL, BORDER_COLOR,
    CYBER_CYAN, NEON_PURPLE, NEON_BLUE,
    STATUS_ONLINE, STATUS_BUSY, STATUS_OFFLINE,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_CYAN, TEXT_EMERALD,
    FONT_TITLE, FONT_SUBTITLE, FONT_CARD_HEADER, FONT_LABEL,
    FONT_BADGE, FONT_MONO, FONT_SMALL
)
from .locales import STRINGS
from ..config import ConfigManager
from ..core.osc_client import VRChatOSCClient
from ..core.translator import TranslationEngine, SUPPORTED_LANGUAGES
from ..core.mic_engine import MicEngine
from ..core.speaker_engine import SpeakerEngine


class AppWindow(ctk.CTk):
    def __init__(self, config: ConfigManager):
        super().__init__()
        self.config = config

        # UI Language: "en" or "tr" (default English for GitHub international standard)
        self.current_locale = self.config.get("ui_lang", "en")

        # Configure Main Window
        self.title(self._t("app_title"))
        self.geometry("1180x760")
        self.minsize(980, 680)
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

        # Translators
        mic_src = SUPPORTED_LANGUAGES.get(self.config.get("mic_source_lang", "Türkçe (tr)"), "tr")
        mic_tgt = SUPPORTED_LANGUAGES.get(self.config.get("mic_target_lang", "English (en)"), "en")
        self.mic_translator = TranslationEngine(default_source=mic_src, default_target=mic_tgt)

        spk_src = SUPPORTED_LANGUAGES.get(self.config.get("speaker_source_lang", "English (en)"), "en")
        spk_tgt = SUPPORTED_LANGUAGES.get(self.config.get("speaker_target_lang", "Türkçe (tr)"), "tr")
        self.speaker_translator = TranslationEngine(default_source=spk_src, default_target=spk_tgt)

        # Engines
        self.mic_engine = MicEngine(
            osc_client=self.osc_client,
            translator=self.mic_translator,
            pause_threshold=self.config.get("mic_pause_threshold", 1.2),
            energy_threshold=self.config.get("mic_energy_threshold", 250),
            stt_lang=mic_src
        )

        self.speaker_engine = SpeakerEngine(
            translator=self.speaker_translator,
            energy_threshold=self.config.get("speaker_energy_threshold", 400),
            pause_threshold=self.config.get("speaker_pause_threshold", 1.0),
            stt_lang=spk_src
        )

        # Build Interface
        self._build_header()
        self._build_main_split()
        self._build_quick_osc_bar()
        self._build_footer()

        # Apply current strings
        self._apply_ui_locale()

        # Start Global Hotkey Listener
        self._start_hotkey_thread()

    def _t(self, key: str) -> str:
        """Helper to get localized string."""
        return STRINGS.get(self.current_locale, STRINGS["en"]).get(key, key)

    # -------------------------------------------------------------
    # UI BUILDERS
    # -------------------------------------------------------------
    def _build_header(self):
        """Top Cyberpunk Header with Status Badges, Language Switcher and OSC Settings"""
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
            hover_color=CYBER_CYAN,
            text_color=TEXT_PRIMARY
        )
        self.topmost_chk.pack(side="right", padx=10)

        # OSC Status Pill
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

    def _build_main_split(self):
        """Two main cards: Left for Mic (You -> VRChat), Right for Speaker (Game -> You)"""
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=16, pady=4)
        container.grid_columnconfigure((0, 1), weight=1)
        container.grid_rowconfigure(0, weight=1)

        # Left: Mic Card
        self.mic_card = self._create_channel_card(
            parent=container,
            col=0,
            title_key="mic_title",
            accent=NEON_PURPLE,
            hotkey_key="mic_hotkey",
            is_mic=True
        )

        # Right: Speaker Card
        self.speaker_card = self._create_channel_card(
            parent=container,
            col=1,
            title_key="speaker_title",
            accent=CYBER_CYAN,
            hotkey_key="speaker_hotkey",
            is_mic=False
        )

    def _create_channel_card(self, parent, col: int, title_key: str, accent: str, hotkey_key: str, is_mic: bool) -> ctk.CTkFrame:
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=12)
        card.grid(row=0, column=col, sticky="nsew", padx=6, pady=4)

        # Card Header
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=14, pady=(12, 6))

        title_lbl = ctk.CTkLabel(top, text=self._t(title_key), font=FONT_CARD_HEADER, text_color=accent)
        title_lbl.pack(side="left")

        hotkey_lbl = ctk.CTkLabel(top, text=self._t(hotkey_key), font=FONT_SMALL, text_color=TEXT_SECONDARY)
        hotkey_lbl.pack(side="right")

        # Status & Toggle Row
        status_row = ctk.CTkFrame(card, fg_color="transparent")
        status_row.pack(fill="x", padx=14, pady=4)

        status_lbl = ctk.CTkLabel(
            status_row,
            text=self._t("status_off"),
            font=FONT_BADGE,
            text_color=STATUS_OFFLINE,
            fg_color="#2D1215",
            corner_radius=6,
            padx=8,
            pady=2
        )
        status_lbl.pack(side="left")

        switch_var = ctk.StringVar(value="off")
        switch = ctk.CTkSwitch(
            status_row,
            text="",
            variable=switch_var,
            onvalue="on",
            offvalue="off",
            progress_color=STATUS_ONLINE,
            command=self._on_mic_toggle if is_mic else self._on_speaker_toggle
        )
        switch.pack(side="right")

        # Language Selection Row
        lang_row = ctk.CTkFrame(card, fg_color="transparent")
        lang_row.pack(fill="x", padx=14, pady=6)

        lang_options = list(SUPPORTED_LANGUAGES.keys())
        default_src = self.config.get("mic_source_lang" if is_mic else "speaker_source_lang")
        default_tgt = self.config.get("mic_target_lang" if is_mic else "speaker_target_lang")

        src_dropdown = ctk.CTkOptionMenu(
            lang_row,
            values=lang_options,
            command=lambda v: self._on_lang_change(is_mic, True, v),
            font=FONT_SMALL,
            fg_color=BG_MAIN,
            button_color=BORDER_COLOR,
            width=150
        )
        src_dropdown.set(default_src)
        src_dropdown.pack(side="left", padx=(0, 4))

        arrow_lbl = ctk.CTkLabel(lang_row, text="➔", font=FONT_LABEL, text_color=CYBER_CYAN)
        arrow_lbl.pack(side="left", padx=4)

        tgt_dropdown = ctk.CTkOptionMenu(
            lang_row,
            values=lang_options,
            command=lambda v: self._on_lang_change(is_mic, False, v),
            font=FONT_SMALL,
            fg_color=BG_MAIN,
            button_color=BORDER_COLOR,
            width=150
        )
        tgt_dropdown.set(default_tgt)
        tgt_dropdown.pack(side="left", padx=(4, 0))

        # Slider / Threshold Control Row
        slider_row = ctk.CTkFrame(card, fg_color="transparent")
        slider_row.pack(fill="x", padx=14, pady=4)

        if is_mic:
            slider_lbl = ctk.CTkLabel(
                slider_row,
                text=f"{self._t('silence_wait')}: {self.config.get('mic_pause_threshold', 1.2)}s",
                font=FONT_SMALL,
                text_color=TEXT_SECONDARY
            )
            slider_lbl.pack(side="left")

            slider = ctk.CTkSlider(
                slider_row,
                from_=0.5,
                to=3.0,
                number_of_steps=25,
                command=lambda v: self._on_mic_slider(slider_lbl, v),
                progress_color=NEON_PURPLE,
                button_color=CYBER_CYAN
            )
            slider.set(self.config.get("mic_pause_threshold", 1.2))
            slider.pack(side="right", fill="x", expand=True, padx=(10, 0))
            self.lbl_mic_title = title_lbl
            self.lbl_mic_hotkey = hotkey_lbl
            self.lbl_mic_pause = slider_lbl
            self.slider_mic_pause = slider
            self.lbl_mic_status = status_lbl
            self.switch_mic_var = switch_var
            self.switch_mic = switch
        else:
            slider_lbl = ctk.CTkLabel(
                slider_row,
                text=f"{self._t('sound_thresh')}: {self.config.get('speaker_energy_threshold', 400)} RMS",
                font=FONT_SMALL,
                text_color=TEXT_SECONDARY
            )
            slider_lbl.pack(side="left")

            slider = ctk.CTkSlider(
                slider_row,
                from_=100,
                to=1500,
                number_of_steps=28,
                command=lambda v: self._on_speaker_slider(slider_lbl, v),
                progress_color=CYBER_CYAN,
                button_color=NEON_BLUE
            )
            slider.set(self.config.get("speaker_energy_threshold", 400))
            slider.pack(side="right", fill="x", expand=True, padx=(10, 0))
            self.lbl_spk_title = title_lbl
            self.lbl_spk_hotkey = hotkey_lbl
            self.lbl_spk_thresh = slider_lbl
            self.slider_spk_thresh = slider
            self.lbl_spk_status = status_lbl
            self.switch_spk_var = switch_var
            self.switch_spk = switch

        # Terminal Log Console
        log_box = ctk.CTkTextbox(
            card,
            font=FONT_MONO,
            fg_color=BG_TERMINAL,
            text_color=TEXT_CYAN,
            border_color=BORDER_COLOR,
            border_width=1,
            corner_radius=8
        )
        log_box.pack(fill="both", expand=True, padx=14, pady=(6, 12))

        if is_mic:
            self.txt_mic_logs = log_box
        else:
            self.txt_spk_logs = log_box

        return card

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
            fg_color="transparent",
            border_color=BORDER_COLOR,
            border_width=1,
            hover_color=BG_CARD,
            text_color=TEXT_SECONDARY,
            height=26,
            command=self._clear_logs
        )
        self.clear_btn.pack(side="right")

    # -------------------------------------------------------------
    # LOCALIZATION CONTROLLER
    # -------------------------------------------------------------
    def _on_ui_lang_change(self, selected: str):
        if "Türkçe" in selected:
            self.current_locale = "tr"
        else:
            self.current_locale = "en"
        self.config.set("ui_lang", self.current_locale)
        self._apply_ui_locale()

    def _apply_ui_locale(self):
        """Updates all UI text elements instantly without app restart."""
        self.title(self._t("app_title"))
        self.title_lbl.configure(text=self._t("header_title"))
        self.subtitle_lbl.configure(text=self._t("header_subtitle"))
        self.topmost_chk.configure(text=self._t("topmost"))

        self.lbl_mic_title.configure(text=self._t("mic_title"))
        self.lbl_mic_hotkey.configure(text=self._t("mic_hotkey"))
        self.lbl_mic_pause.configure(text=f"{self._t('silence_wait')}: {self.config.get('mic_pause_threshold', 1.2)}s")

        self.lbl_spk_title.configure(text=self._t("speaker_title"))
        self.lbl_spk_hotkey.configure(text=self._t("speaker_hotkey"))
        self.lbl_spk_thresh.configure(text=f"{self._t('sound_thresh')}: {self.config.get('speaker_energy_threshold', 400)} RMS")

        self.quick_label.configure(text=self._t("quick_label"))
        self.quick_send_btn.configure(text=self._t("quick_send_btn"))
        self.quick_input.configure(placeholder_text=self._t("quick_placeholder"))

        self.info_lbl.configure(text=self._t("tip_info"))
        self.clear_btn.configure(text=self._t("clear_logs_btn"))

        # Update active statuses
        if self.switch_mic_var.get() == "on":
            self.lbl_mic_status.configure(text=self._t("status_on"))
        else:
            self.lbl_mic_status.configure(text=self._t("status_off"))

        if self.switch_spk_var.get() == "on":
            self.lbl_spk_status.configure(text=self._t("status_on"))
        else:
            self.lbl_spk_status.configure(text=self._t("status_off"))

    # -------------------------------------------------------------
    # EVENT HANDLERS & LOGIC
    # -------------------------------------------------------------
    def _toggle_topmost(self):
        val = self.topmost_var.get()
        self.attributes("-topmost", val)
        self.config.set("always_on_top", val)

    def _on_lang_change(self, is_mic: bool, is_source: bool, value: str):
        code = SUPPORTED_LANGUAGES.get(value, "en")
        if is_mic:
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
        else:
            if is_source:
                self.config.set("speaker_source_lang", value)
                self.speaker_engine.set_stt_language(code)
            else:
                self.config.set("speaker_target_lang", value)
            src = SUPPORTED_LANGUAGES.get(self.config.get("speaker_source_lang"), "en")
            tgt = SUPPORTED_LANGUAGES.get(self.config.get("speaker_target_lang"), "tr")
            self.speaker_translator.set_languages(src, tgt)
            msg = self._t("lang_changed_spk").format(src=src, tgt=tgt)
            self.log_speaker(msg)

    def _on_mic_slider(self, label, value):
        rounded = round(float(value), 1)
        label.configure(text=f"{self._t('silence_wait')}: {rounded}s")
        self.mic_engine.set_pause_threshold(rounded)
        self.config.set("mic_pause_threshold", rounded)

    def _on_speaker_slider(self, label, value):
        val = int(value)
        label.configure(text=f"{self._t('sound_thresh')}: {val} RMS")
        self.speaker_engine.set_energy_threshold(val)
        self.config.set("speaker_energy_threshold", val)

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
        self.txt_spk_logs.delete("1.0", "end")

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
    # SPEAKER CHANNEL LOGIC
    # -------------------------------------------------------------
    def _on_speaker_toggle(self):
        if self.switch_spk_var.get() == "on":
            self.lbl_spk_status.configure(text=self._t("status_busy"), text_color=STATUS_BUSY, fg_color="#332205")
            self.switch_spk.configure(state="disabled")
            threading.Thread(target=self._start_speaker_worker, daemon=True).start()
        else:
            self.speaker_engine.stop_listening()
            self.lbl_spk_status.configure(text=self._t("status_off"), text_color=STATUS_OFFLINE, fg_color="#2D1215")
            self.log_speaker(self._t("speaker_stopped"))

    def _start_speaker_worker(self):
        try:
            self.speaker_engine.start_listening(
                on_translation=lambda src, trans: self.after(0, self._on_speaker_result, src, trans),
                on_status=lambda st: self.after(0, self.log_speaker, st)
            )
            self.after(0, self._ui_speaker_started)
        except Exception as e:
            self.after(0, self._ui_speaker_failed, str(e))

    def _ui_speaker_started(self):
        self.switch_spk.configure(state="normal")
        self.lbl_spk_status.configure(text=self._t("status_on"), text_color=STATUS_ONLINE, fg_color="#0D281E")

    def _ui_speaker_failed(self, err: str):
        self.switch_spk.configure(state="normal")
        self.switch_spk_var.set("off")
        self.lbl_spk_status.configure(text=self._t("status_err"), text_color=STATUS_OFFLINE, fg_color="#2D1215")
        self.log_speaker(f"🔴 Error: {err}")

    def _on_speaker_result(self, src: str, trans: str):
        ts = time.strftime("%H:%M:%S")
        self.log_speaker(f"[{ts}] {self._t('other_label')}: {src}")
        self.log_speaker(f"[{ts}] {self._t('tr_label')}: {trans}\n")

    def log_speaker(self, msg: str):
        self.txt_spk_logs.insert("end", f"{msg}\n")
        self.txt_spk_logs.see("end")

    # -------------------------------------------------------------
    # GLOBAL HOTKEYS (F4 & F5)
    # -------------------------------------------------------------
    def _start_hotkey_thread(self):
        t = threading.Thread(target=self._hotkey_listener_loop, daemon=True, name="HotkeyThread")
        t.start()

    def _hotkey_listener_loop(self):
        """Asynchronous Windows hotkey polling via GetAsyncKeyState (VK_F4=0x73, VK_F5=0x74)"""
        VK_F4 = 0x73
        VK_F5 = 0x74
        f4_down = False
        f5_down = False

        while True:
            try:
                # Check F4 (Mic Toggle)
                is_f4 = bool(ctypes.windll.user32.GetAsyncKeyState(VK_F4) & 0x8000)
                if is_f4 and not f4_down:
                    f4_down = True
                    self.after(0, self._toggle_mic_hotkey)
                elif not is_f4:
                    f4_down = False

                # Check F5 (Speaker Toggle)
                is_f5 = bool(ctypes.windll.user32.GetAsyncKeyState(VK_F5) & 0x8000)
                if is_f5 and not f5_down:
                    f5_down = True
                    self.after(0, self._toggle_speaker_hotkey)
                elif not is_f5:
                    f5_down = False

            except Exception:
                pass
            time.sleep(0.06)

    def _toggle_mic_hotkey(self):
        current = self.switch_mic_var.get()
        new_val = "off" if current == "on" else "on"
        self.switch_mic_var.set(new_val)
        self._on_mic_toggle()

    def _toggle_speaker_hotkey(self):
        current = self.switch_spk_var.get()
        new_val = "off" if current == "on" else "on"
        self.switch_spk_var.set(new_val)
        self._on_speaker_toggle()
