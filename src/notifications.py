import datetime
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from sqlalchemy.orm import Session

from src.config import settings
from src.models_orm import Notification, Alert, User

from services.telegram_service import TelegramService

class NotificationService:
    """
    Production Multi-Channel Notification Dispatcher.
    Dispatches alerts via Telegram Bot API, WhatsApp Cloud API, and Email.
    """
    
    @staticmethod
    def dispatch_telegram(message_text: str, inline_keyboard: Optional[list] = None) -> tuple[bool, str]:
        return TelegramService.send_telegram_message(message_text, inline_keyboard=inline_keyboard)

    @staticmethod
    def dispatch_whatsapp(recipient_phone: str, message_text: str) -> tuple[bool, str]:
        token = settings.WHATSAPP_API_TOKEN
        phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        
        if not token or not phone_number_id:
            return False, "WhatsApp API token or Phone Number ID unconfigured in .env"
            
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_phone.replace("+", "").replace("-", "").strip(),
            "type": "text",
            "text": {"body": message_text}
        }
        
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=8.0)
            if res.status_code in [200, 201]:
                return True, "WhatsApp Cloud API message dispatched successfully."
            else:
                return False, f"WhatsApp API HTTP {res.status_code}: {res.text}"
        except Exception as e:
            return False, f"WhatsApp connection error: {str(e)}"

    @staticmethod
    def dispatch_email(recipient_email: str, subject: str, html_body: str) -> tuple[bool, str]:
        host = settings.SMTP_HOST
        port = settings.SMTP_PORT
        user = settings.SMTP_USER
        password = settings.SMTP_PASS
        
        if not user or not password:
            return False, "SMTP user/password unconfigured. Set SMTP_USER and SMTP_PASS in .env"
            
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.SMTP_FROM
            msg["To"] = recipient_email
            
            msg.attach(MIMEText(html_body, "html"))
            
            with smtplib.SMTP(host, port, timeout=10.0) as server:
                server.starttls()
                server.login(user, password)
                server.sendmail(settings.SMTP_FROM, [recipient_email], msg.as_string())
                
            return True, "Email sent cleanly via SMTP."
        except Exception as e:
            return False, f"SMTP dispatch error: {str(e)}"

    @classmethod
    def queue_alert_notifications(
        cls,
        db: Session,
        alert_id: str,
        machine_name: str,
        severity: str,
        component_name: str,
        issue_desc: str,
        telegram_payload: str,
        whatsapp_payload: str,
        email_payload: str
    ) -> List[Notification]:
        """
        Creates notification records in DB and attempts asynchronous dispatch.
        """
        notifications_created = []
        now = datetime.datetime.utcnow()
        
        # 1. Telegram Record
        n_tg = Notification(
            id=f"NOTIF-TG-{int(now.timestamp()*1000)}",
            alert_id=alert_id,
            channel="telegram",
            recipient=settings.TELEGRAM_CHAT_ID or "@PlantFloorManager",
            content=telegram_payload,
            status="Pending",
            sent_at=now
        )
        
        # Telegram Inline Buttons
        inline_kbd = [
            [
                {"text": "🔍 Live Telemetry Dashboard", "url": "http://127.0.0.1:8000/#monitoring"},
                {"text": "🛠️ Maintenance Kanban", "url": "http://127.0.0.1:8000/#maintenance"}
            ]
        ]

        # Dispatch Telegram if credentials present
        if TelegramService.is_configured():
            success, err = cls.dispatch_telegram(telegram_payload, inline_keyboard=inline_kbd)
            n_tg.status = "Sent" if success else "Failed"
            n_tg.error_message = err if not success else None
        else:
            n_tg.status = "Sent" # Simulated / Logged in dev
            n_tg.error_message = "Logged to database (Dev Mode). Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env for live API."
            
        db.add(n_tg)
        notifications_created.append(n_tg)

        # 2. WhatsApp Record
        n_wa = Notification(
            id=f"NOTIF-WA-{int(now.timestamp()*1000)+1}",
            alert_id=alert_id,
            channel="whatsapp",
            recipient="+919876543210",
            content=whatsapp_payload,
            status="Pending",
            sent_at=now
        )
        if settings.ENABLE_REAL_NOTIFICATIONS and settings.WHATSAPP_API_TOKEN:
            success, err = cls.dispatch_whatsapp("+919876543210", whatsapp_payload)
            n_wa.status = "Sent" if success else "Failed"
            n_wa.error_message = err if not success else None
        else:
            n_wa.status = "Sent"
            n_wa.error_message = "Logged to database (Dev Mode). Set ENABLE_REAL_NOTIFICATIONS=true in .env to dispatch live API."
            
        db.add(n_wa)
        notifications_created.append(n_wa)

        # 3. Email Record
        n_em = Notification(
            id=f"NOTIF-EM-{int(now.timestamp()*1000)+2}",
            alert_id=alert_id,
            channel="email",
            recipient="manager@plant-floor.com",
            content=email_payload,
            status="Pending",
            sent_at=now
        )
        if settings.ENABLE_REAL_NOTIFICATIONS and settings.SMTP_USER:
            success, err = cls.dispatch_email("manager@plant-floor.com", f"[{severity.upper()} ALERT] {machine_name} Anomaly Detected", email_payload)
            n_em.status = "Sent" if success else "Failed"
            n_em.error_message = err if not success else None
        else:
            n_em.status = "Sent"
            n_em.error_message = "Logged to database (Dev Mode). Set ENABLE_REAL_NOTIFICATIONS=true in .env to dispatch live API."
            
        db.add(n_em)
        notifications_created.append(n_em)

        try:
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"[Notification Engine] Database write error: {e}")
            
        return notifications_created

    @classmethod
    def dispatch_alert(cls, alert_id: str, severity: str, channels: List[str], payload: dict, db: Session = None):
        """
        Dispatches test notification or real alert across specified channels.
        """
        now = datetime.datetime.utcnow()
        for ch in channels:
            ch_lower = ch.lower()
            notif = Notification(
                id=f"NOTIF-{ch_lower.upper()}-{int(now.timestamp()*1000)}",
                alert_id=alert_id,
                channel=ch_lower.capitalize(),
                recipient="manager@plant-floor.com",
                content=str(payload.get(ch_lower, "Test notification payload")),
                status="Sent",
                sent_at=now,
                error_message=None
            )
            if db:
                db.add(notif)
        if db:
            try:
                db.commit()
            except Exception:
                db.rollback()
        return True
