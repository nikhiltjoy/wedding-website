from enum import Enum
from typing import Dict, List, Optional, Mapping


class ContactMethod(Enum):
    INVALID = 0
    EMAIL = 1
    WHATSAPP = 2
    INSTAGRAM = 3
    MESSENGER = 4

    @staticmethod
    def from_str(label: str):
        label_to_check = "" if not label else label
        return ContactMethod.__dict__.get(label_to_check.upper(), ContactMethod.INVALID)


class Guest:
    def __init__(self, user_record: Dict):
        self.party_id: int = user_record.get("party_id")
        self.user_id: int = user_record.get("user_id")
        self.first_name: str = user_record.get("user_first_name")
        self.last_name: str = user_record.get("user_last_name")
        self.is_primary: bool = user_record.get("is_primary_user")
        self.is_invited_sydney: bool = user_record.get("is_invited_sydney")
        self.is_invited_india: bool = user_record.get("is_invited_india")
        self.is_coming_sydney: bool = user_record.get("is_coming_sydney")
        self.is_coming_india: bool = user_record.get("is_coming_india")
        self.is_placeholder: bool = user_record.get("is_placeholder")
        self.preferred_contact_method: ContactMethod = ContactMethod.from_str(
            user_record.get("user_preferred_contact")
        )
        self.email: str = user_record.get("user_email")
        self.whatsapp: str = user_record.get("user_whatsapp")
        self.instagram: str = user_record.get("user_instagram")
        self.messenger: str = user_record.get("user_messenger")

    def __repr__(self):
        return (
            f"User ID: {self.user_id}\n"
            f"Name: {self.first_name} {self.last_name}\n"
            f"Party Head: {self.is_primary}\n"
            f"Is Placeholder: {self.is_placeholder}\n"
            f"Is Invited [Sydney]: {self.is_invited_sydney}\n"
            f"Is Invited [India]: {self.is_invited_india}\n"
            f"Is Coming [Sydney]: {self.is_coming_sydney}\n"
            f"Is Coming [India]: {self.is_coming_india}\n"
            f"Contact Method: {self.preferred_contact_method}\n"
            f"Email: {self.email}\n"
            f"WhatsApp: {self.whatsapp}\n"
            f"Instagram: {self.instagram}\n"
            f"Messenger: {self.messenger}"
        )


class Party:
    def __init__(self, guests: List[Guest]):
        self.party_id: int = guests[0].party_id
        self.primary_guest: Optional[Guest] = None
        self._guests: Mapping[int, Guest] = {}
        for i, g in enumerate(guests):
            if g.is_primary:
                self.primary_guest = g
                if 0 in self._guests:
                    _tmp = self._guests[0]
                    self._guests[0] = g
                    self._guests[i] = _tmp
                else:
                    self._guests[i] = g
            else:
                self._guests[i] = g

    def get_first_names(self) -> str:
        total_guests = len(self._guests)
        guest_names = [
            self._guests[i].first_name
            for i in range(total_guests)
            if not self._guests[i].is_placeholder
        ]
        if len(guest_names) == 1:
            return guest_names[0]
        last_guest_name = guest_names[-1]
        return ", ".join(guest_names[:-1]) + " and " + last_guest_name

    def _get_prioritized_guests(self) -> List[Guest]:
        total_guests = len(self._guests)
        return [self._guests[i] for i in range(total_guests)]

    def get_guests(self) -> List[Guest]:
        return self._get_prioritized_guests()

    def __repr__(self):
        return (
            f"Party ID: {self.party_id}\nParty Size: {len(self._guests)}\n"
            f"Primary Guest: {self.primary_guest.first_name} "
            f"{self.primary_guest.last_name}"
        )
