from pathlib import Path
from typing import List, Optional

from fbchat._session import session_factory

from outreach.message.BaseMessageClient import BaseMessageClient
from pymessenger.bot import Bot
from outreach.models.party import Party
from fbchat import Client


class MessengerMessageClient(BaseMessageClient):
    def __init__(self, bot_token: str):
        self.client = Bot(bot_token)
        self.client.base_url = f"https://graph.facebook.com/v15.0/me/messages?" \
                               f"access_token={bot_token}"

    def send_message(
        self,
        party: Party,
        message: str,
        subject: str = "",
        img_paths: Optional[List[Path]] = None,
    ):
        Client(session=session_factory())
        recipients_set = [g.messenger for g in party.get_guests() if g.messenger]
        if len(recipients_set) > 1:
            group_id = self._create_messenger_group(recipients_set)
        else:
            group_id = list(recipients_set)[0]
        if not img_paths:
            self._send_text_message(group_id, message)
        else:
            self._send_img_message(group_id, img_paths, message)

    def _send_text_message(self, recipient: str, message: str = "This is a test"):
        print(f"Sending message to {recipient}")
        self.client.send_message(recipient_id=recipient, message=message)

    def _send_img_message(
        self, recipient: str, img_paths: List[Path], message: str = ""
    ):
        for img_path in img_paths:
            self.client.send_image(
                recipient_id=recipient, image_path=str(img_path.resolve())
            )
        self._send_text_message(recipient, message)

    @staticmethod
    def _create_messenger_group(recipients: List[str]) -> str:
        print("WhatsApp Group Creation to be implemented")
        return recipients[0]
