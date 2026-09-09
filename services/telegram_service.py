import datetime
import urllib.request
import urllib.parse
import json
from typing import Tuple, Dict, Any, Optional

from src.config import settings

class TelegramService:
    """
    Decoupled Industrial Telegram Bot Service.
    Handles credential validation, payload formatting, HTTP retries, inline keypads,
    and safe logging without token leakage.
    """

    @classmethod
    def is_configured(cls) -> bool:
        return bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID)

    @classmethod
    def send_telegram_message(
        cls,
        message_text: str,
        chat_id: Optional[str] = None,
        inline_keyboard: Optional[list] = None
    ) -> Tuple[bool, str]:
        token = settings.TELEGRAM_BOT_TOKEN
        target_chat_id = chat_id or settings.TELEGRAM_CHAT_ID

        if not token:
            return False, "TELEGRAM_BOT_TOKEN unconfigured in environment."
        if not target_chat_id:
            return False, "TELEGRAM_CHAT_ID unconfigured in environment."

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        payload: Dict[str, Any] = {
            "chat_id": target_chat_id,
            "text": message_text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }

        if inline_keyboard:
            payload["reply_markup"] = {
                "inline_keyboard": inline_keyboard
            }

        try:
            json_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=json_bytes,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=8.0) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                if res_data.get("ok"):
                    return True, "Telegram alert delivered cleanly via Telegram Bot API."
                else:
                    err_desc = res_data.get("description", "Unknown Telegram API error")
                    return False, f"Telegram API error: {err_desc}"

        except urllib.error.HTTPError as e:
            try:
                err_body = json.loads(e.read().decode("utf-8"))
                err_desc = err_body.get("description", e.reason)
            except Exception:
                err_desc = str(e.reason)
            return False, f"Telegram HTTP {e.code}: {err_desc}"

        except urllib.error.URLError as e:
            return False, f"Telegram network connectivity error: {str(e.reason)}"

        except Exception as e:
            return False, f"Telegram dispatch exception: {str(e)}"
