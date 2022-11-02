from collections import defaultdict
from jinja2 import Template
from pathlib import Path
from typing import Dict, Mapping, List

from outreach.message.EmailMessageClient import (
    get_wedding_name,
    EmailMessageClient,
    get_random_names,
)
from outreach.message.MessengerMessageClient import MessengerMessageClient
from outreach.models.party import Party, Guest
import pandas as pd
import numpy as np


class WeddingParty:
    def __init__(
        self,
        data_dir: Path,
        wedding_props: Dict,
    ):
        self.data_dir = data_dir
        self.save_the_date_paths = {
            p.stem: p
            for p in (self.data_dir / "images" / "save_the_dates").iterdir()
            if p.is_file()
        }
        self.all_parties: Mapping[int, Party] = {}
        self.all_guests: Mapping[int, Guest] = {}
        self.wedding_props = wedding_props
        guest_df = pd.read_csv(
            (self.data_dir / "guests_db.csv"),
            dtype={"user_whatsapp": str, "user_messenger": str},
        ).replace([np.nan], [None])
        _tmp_parties: Mapping[int, List[Guest]] = defaultdict(list)
        for i, row in guest_df.iterrows():
            guest = Guest(row.to_dict())
            self.all_guests[guest.user_id] = guest
            _tmp_parties[guest.party_id].append(guest)
        for p in _tmp_parties:
            self.all_parties[p] = Party(_tmp_parties[p])

    def get_guest(self, user_id: int):
        return self.all_guests.get(user_id)

    def get_party(self, party_id: int):
        return self.all_parties.get(party_id)

    def send_save_the_date_email(self, email_client: EmailMessageClient, party: Party):
        email_vars = {
            "subject": f"[{get_wedding_name()}] Hi {party.get_first_names()}!",
            "names": party.get_first_names(),
            "is_invited_india": party.primary_guest.is_invited_india,
            "is_invited_sydney": party.primary_guest.is_invited_sydney,
            "num_guests": len(party.get_guests())
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

        email_client.send_message(
            party=party,
            message=msg,
            subject=email_vars["subject"],
            img_paths=files_to_send,
        )

    def send_save_the_date_messenger(
        self, messenger_client: MessengerMessageClient, party: Party
    ):
        def _sydney_msg():
            msg = (
                f"Hey {party.get_first_names()},\nWe'd love for you to attend"
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
                f"Hey {party.get_first_names()},\nWe'd love for you to attend"
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
                f"Hey {party.get_first_names()},\nWe'd love for you to attend"
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

        messenger_client.send_message(party=party, message=msg, img_paths=files_to_send)
