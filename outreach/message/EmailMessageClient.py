import random
import re
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from pathlib import Path
from typing import List, Optional

from outreach.message.BaseMessageClient import BaseMessageClient
from outreach.models.party import Party

GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587


def get_random_names() -> str:
    names = ["Nikhil", "Joanne"]
    # random.shuffle(names)
    return '+'.join(names)


def get_wedding_name() -> str:
    return f"{get_random_names()}'s Wedding"


def get_default_email_subject() -> str:
    return f"[Update] {get_wedding_name()}"


def check_if_valid_email(test_email) -> bool:
    if not test_email:
        return False
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    return bool(re.fullmatch(regex, test_email))


class EmailMessageClient(BaseMessageClient):
    def __init__(self, sender_email, sender_pw):
        context = ssl.create_default_context()
        self.server = smtplib.SMTP(GMAIL_SMTP_HOST, GMAIL_SMTP_PORT)
        self.sender_email = sender_email
        self.server.connect(GMAIL_SMTP_HOST, GMAIL_SMTP_PORT)
        self.server.ehlo()
        self.server.starttls(context=context)
        self.server.ehlo()
        self.server.login(sender_email, sender_pw)
        self.server.ehlo()

    def send_message(
        self,
        party: Party,
        message: str,
        subject: str = get_default_email_subject(),
        img_paths: Optional[List[Path]] = None,
    ):
        valid_emails = []
        for email in [g.email for g in party.get_guests()]:
            if not check_if_valid_email(email):
                print(f"Invalid Email: {email}")
                continue
            valid_emails.append(email)
        if not valid_emails:
            return
        self._send_plaintext_email(
            recipients=valid_emails,
            message=message,
            files=img_paths,
            subject=subject
        )

    def _send_plaintext_email(
        self,
        recipients: List[str],
        message: str = "This is a test",
        subject: str = "",
        files: Optional[List[Path]] = None,
    ):
        msg = MIMEMultipart()
        msg['From'] = f"{get_random_names()} {self.sender_email}"
        msg['To'] = ', '.join(recipients)
        msg['Date'] = formatdate(localtime=True)
        msg["subject"] = subject
        if message.endswith("</html>"):
            msg.attach(MIMEText(message, "html"))
        else:
            msg.attach(MIMEText(message, "plain"))
        if files:
            for path in files:
                part = MIMEBase('application', "octet-stream")
                with open(path, 'rb') as file:
                    part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition',
                                'attachment; filename={}'.format(path.name))
                msg.attach(part)
        self.server.sendmail(
            from_addr=self.sender_email, to_addrs=recipients, msg=msg.as_bytes()
        )
