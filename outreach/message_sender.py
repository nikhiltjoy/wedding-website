from pathlib import Path

from jinja2 import Template

from outreach.message.EmailMessageClient import (
    EmailMessageClient,
    get_wedding_name,
    get_random_names,
)
from outreach.message.MessengerMessageClient import MessengerMessageClient
from outreach.models.party import Party


class MessageSender:
    def __init__(
        self,
        data_dir: Path,
        email_client: EmailMessageClient = None,
        messenger_client: MessengerMessageClient = None,
    ):
        self.data_dir = data_dir
        self.email_client = email_client
        self.messenger_client = messenger_client
        self.save_the_date_paths = {
            p.stem: p
            for p in (self.data_dir / "images" / "save_the_dates").iterdir()
            if p.is_file()
        }

    def send_save_the_date_email(self, party: Party):
        email_vars = {
            "subject": f"[{get_wedding_name()}] Hi {party.get_friendly_names()}!",
            "names": party.get_friendly_names(),
            "is_invited_india": party.primary_guest.is_invited_india,
            "is_invited_sydney": party.primary_guest.is_invited_sydney,
            "num_guests": len(party.get_guests()),
        }
        email_template_dir = self.data_dir / "templates" / "email" / "save_the_date"

        files_to_send = []
        email_template_name = "template.html"

        if (
            party.primary_guest.is_invited_india
            and party.primary_guest.is_invited_sydney
        ):
            files_to_send = list(self.save_the_date_paths.values())
        elif party.primary_guest.is_invited_sydney:
            files_to_send = [self.save_the_date_paths["sydney"]]
        elif party.primary_guest.is_invited_india:
            files_to_send = [self.save_the_date_paths["india"]]

        if not files_to_send:
            return

        with open(email_template_dir / email_template_name) as f:
            msg = Template(f.read()).render(**email_vars)

        sent_email_guests = self.email_client.send_message(
            party=party,
            message=msg,
            subject=email_vars["subject"],
            img_paths=files_to_send,
        )
        for g in sent_email_guests:
            g.save_the_date_email_invited += 1

    def send_save_the_date_messenger(self, party: Party):
        def _sydney_msg():
            msg = (
                f"Hey {party.get_friendly_names()},\nWe'd love for you to attend"
                f" our wedding in Sydney on Saturday, October 7, 2023. Please "
                f"find the attached save the date.\n\nPlease email us if you can't"
                f" make it!\n\nWe'll be sending out formal invitations soon,"
                f" and an official website is in the works.\n\n"
            )
            if len(party.get_guests()) > 2:
                msg = msg + "Looking forward to celebrating with all of you!\n\n"
            elif len(party.get_guests()) == 2:
                msg = msg + "Looking forward to celebrating with both of you!\n\n"
            else:
                msg = msg + "Looking forward to celebrating with you!\n\n"
            return msg + f"Best,\n{get_random_names()}"

        def _india_msg():
            msg = (
                f"Hey {party.get_friendly_names()},\nWe'd love for you to attend"
                f" our wedding in Kochi, India on Sunday, October 15, 2023. Please"
                f" find the attached save the date.\n\nPlease email us if you"
                f" can't make it!\n\nWe'll be sending out formal invitations soon,"
                f" and an official website is in the works.\n\n"
            )
            if len(party.get_guests()) > 2:
                msg = msg + "Looking forward to celebrating with all of you!\n\n"
            elif len(party.get_guests()) == 2:
                msg = msg + "Looking forward to celebrating with both of you!\n\n"
            else:
                msg = msg + "Looking forward to celebrating with you!\n\n"
            return msg + f"Best,\n{get_random_names()}"

        def _both_msg():
            msg = (
                f"Hey {party.get_friendly_names()},\nWe'd love for you to attend"
                f" our wedding in Sydney, Australia on Saturday, October 7, 2023"
                f" and Kochi, India on Sunday, October 15, 2023. Please"
                f" find the attached save the dates.\n\nPlease let us know "
                f"what your availability is! We realize attending two"
                f' "destination" weddings is a big commitment,'
                f" and we appreciate you! Let us know if you can come to either/"
                f"both!\n\nWe'll be sending out formal invitations soon,"
                f" and an official website is in the works.\n\n"
            )
            if len(party.get_guests()) > 2:
                msg = msg + "Looking forward to celebrating with all of you!\n\n"
            elif len(party.get_guests()) == 2:
                msg = msg + "Looking forward to celebrating with both of you!\n\n"
            else:
                msg = msg + "Looking forward to celebrating with you!\n\n"
            return msg + f"Best,\n{get_random_names()}"

        msg = ""
        files_to_send = []

        if (
            party.primary_guest.is_invited_india
            and party.primary_guest.is_invited_sydney
        ):
            msg = _both_msg()
            files_to_send = list(self.save_the_date_paths.values())
        elif party.primary_guest.is_invited_sydney:
            msg = _sydney_msg()
            files_to_send = [self.save_the_date_paths["sydney"]]
        elif party.primary_guest.is_invited_india:
            msg = _india_msg()
            files_to_send = [self.save_the_date_paths["india"]]

        if not msg:
            return

        self.messenger_client.send_message(
            party=party, message=msg, img_paths=files_to_send
        )
