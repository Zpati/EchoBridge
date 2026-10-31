"""
VRChat OSC Client Module
Handles Open Sound Control (OSC) communication with VRChat Chatbox API.
Complies with official VRChat OSC specifications:
- Address: /chatbox/input [message: str, complete: bool, notify: bool]
- Address: /chatbox/typing [typing: bool]
"""

import time
import logging
from typing import Optional, Callable
from pythonosc import udp_client

logger = logging.getLogger("VRChatOSC")


class VRChatOSCClient:
    def __init__(self, ip: str = "127.0.0.1", port: int = 9000, typing_delay: float = 0.05):
        self.ip = ip
        self.port = int(port)
        self.typing_delay = typing_delay
        self.client: Optional[udp_client.SimpleUDPClient] = None
        self._init_client()

    def _init_client(self):
        try:
            self.client = udp_client.SimpleUDPClient(self.ip, self.port)
            logger.info(f"[OSC] Initialized client for {self.ip}:{self.port}")
        except Exception as e:
            logger.error(f"[OSC Error] Failed to bind client: {e}")
            self.client = None

    def update_endpoint(self, ip: str, port: int):
        self.ip = ip
        self.port = int(port)
        self._init_client()

    def set_typing(self, is_typing: bool):
        """Sends typing indicator to VRChat chatbox bubble."""
        if not self.client:
            return
        try:
            self.client.send_message("/chatbox/typing", is_typing)
        except Exception as e:
            logger.warning(f"[OSC] Typing indicator error: {e}")

    def send_chatbox_message(
        self,
        message: str,
        typing_indicator: bool = True,
        play_sound: bool = True,
        log_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        Sends a message to VRChat chatbox.
        VRChat /chatbox/input signature: [message_string, complete_flag, notification_sound]
        """
        if not self.client:
            self._init_client()
            if not self.client:
                if log_callback:
                    log_callback("[OSC Hata] İstemci başlatılamadı.")
                return False

        message = message.strip()
        if not message:
            return False

        try:
            # Show typing bubble momentarily for natural effect
            if typing_indicator:
                self.set_typing(True)
                time.sleep(self.typing_delay)

            # Send payload: [message, True (send immediately), play_sound (beep sound)]
            self.client.send_message("/chatbox/input", [message, True, play_sound])
            
            if typing_indicator:
                self.set_typing(False)

            log_msg = f"[OSC] VRChat Chatbox'a Gönderildi: {message}"
            logger.info(log_msg)
            if log_callback:
                log_callback(log_msg)
            return True

        except Exception as e:
            err_msg = f"[OSC Hata] Mesaj gönderilemedi: {e}"
            logger.error(err_msg)
            if log_callback:
                log_callback(err_msg)
            return False
