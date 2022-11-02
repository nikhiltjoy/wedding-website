from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from outreach.message.BaseMessageClient import BaseMessageClient
import pywhatkit

from outreach.models.party import Party


class WhatsAppMessageClient(BaseMessageClient):
    def __init__(self):
        pass

    def send_message(
        self,
        party: Party,
        message: str,
        subject: str = "",
        img_paths: Optional[List[Path]] = None,
    ):
        recipients_set = [g.whatsapp for g in party.get_guests() if g.whatsapp]
        if len(recipients_set) > 1:
            group_id = self._create_whatsapp_group(recipients_set)
        else:
            group_id = list(recipients_set)[0]
        if not img_paths:
            if len(party.get_guests()) == 1 and group_id.startswith("+"):
                self._send_text_message_to_user(group_id, message)
            else:
                self._send_text_message_to_group(group_id, message)
        else:
            self.send_img_message(group_id, img_paths, message)

    @staticmethod
    def _send_text_message_to_user(recipient: str, message: str = "This is a test"):
        pywhatkit.sendwhatmsg_instantly(
            phone_no=recipient, message=message, tab_close=True
        )

    @staticmethod
    def _send_text_message_to_group(recipient: str, message: str = "This is a test"):
        now = datetime.now() + timedelta(minutes=1)
        pywhatkit.sendwhatmsg_to_group(
            group_id=recipient,
            message=message,
            time_hour=now.hour,
            time_min=now.minute,
            tab_close=True,
        )

    @staticmethod
    def send_img_message(recipient: str, img_paths: List[Path], message: str = ""):
        sent_caption = False
        for img_path in img_paths:
            pywhatkit.sendwhats_image(
                receiver=recipient,
                img_path=str(img_path.resolve()),
                caption=message if not sent_caption else "",
                tab_close=True,
            )
            sent_caption = True

    @staticmethod
    def _create_whatsapp_group(recipients: List[str]) -> str:
        print("WhatsApp Group Creation to be implemented")
        return recipients[0]
