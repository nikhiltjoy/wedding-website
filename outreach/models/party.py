from enum import Enum
from typing import Dict, List, Optional, Mapping, Any


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


def check_numeric(x):
    try:
        float(x)
        return True
    except:
        return False


def _parse_whatsapp(value):
    if check_numeric(value):
        value_str = str(value).replace(".0", "")
        return f"+{value_str}"
    return str_cleanse(value, True)


def _parse_messenger(value):
    if check_numeric(value):
        value_str = str(value).replace(".0", "")
        return value_str
    return str_cleanse(value, True)


class Guest:
    def __init__(self, user_record: Dict):
        self.party_id: int = int(user_record.get("party_id"))
        self.user_id: int = int(user_record.get("user_id"))
        self.friendly_name: str = str_cleanse(
            user_record.get("user_friendly_name", "")
        )
        self.first_name: str = str_cleanse(user_record.get("user_first_name", ""))
        self.last_name: str = str_cleanse(user_record.get("user_last_name", ""))
        self.is_primary: bool = bool(user_record.get("is_primary_user", False))
        self.is_invited_sydney: bool = bool(user_record.get("is_invited_sydney", False))
        self.is_invited_india: bool = bool(user_record.get("is_invited_india", False))
        self.is_coming_sydney: bool = bool(user_record.get("is_coming_sydney", False))
        self.is_coming_india: bool = bool(user_record.get("is_coming_india", False))
        self.is_placeholder: bool = bool(user_record.get("is_placeholder", True))
        self.chinese_message: bool = bool(user_record.get("chinese_message", False))
        self.preferred_contact_method: ContactMethod = ContactMethod.from_str(
            str(user_record.get("user_preferred_contact"))
        )
        self.email: str = str_cleanse(user_record.get("user_email", ""), True)
        self.whatsapp: str = _parse_whatsapp(user_record.get("user_whatsapp", ""))
        self.instagram: str = str_cleanse(user_record.get("user_instagram", ""), True)
        self.messenger: str = _parse_messenger(user_record.get("user_messenger", ""))
        self.country: str = str_cleanse(user_record.get("user_country", ""), True)
        self.invite_method: ContactMethod = ContactMethod.from_str(
            str(user_record.get("user_invite_method"))
        )
        self.update_method: ContactMethod = ContactMethod.from_str(
            str(user_record.get("user_update_method"))
        )
        self.save_the_date_email_invited: int = int(
            user_record.get("save_the_date_email_invited", 0)
        )

    def get_guest_as_dict(self):
        return {
            "party_id": self.party_id,
            "user_id": self.user_id,
            "user_friendly_name": self.friendly_name,
            "user_first_name": self.first_name,
            "user_last_name": self.last_name,
            "is_primary_user": self.is_primary,
            "is_invited_sydney": self.is_invited_sydney,
            "is_invited_india": self.is_invited_india,
            "is_coming_sydney": self.is_coming_sydney,
            "is_coming_india": self.is_coming_india,
            "is_placeholder": self.is_placeholder,
            "chinese_message": self.chinese_message,
            "user_preferred_contact": self.preferred_contact_method.name,
            "user_email": self.email,
            "user_whatsapp": self.whatsapp,
            "user_instagram": self.instagram,
            "user_messenger": self.messenger,
            "user_country": self.country,
            "user_invite_method": self.invite_method.name,
            "user_update_method": self.update_method.name,
            "save_the_date_email_invited": self.save_the_date_email_invited,
        }

    def __repr__(self):
        return (
            f"User ID: {self.user_id}\n"
            f"Friendly Name: {self.friendly_name}\n"
            f"Name: {self.first_name} {self.last_name}\n"
            f"Party Head: {self.is_primary}\n"
            f"Is Placeholder: {self.is_placeholder}\n"
            f"Is Invited [Sydney]: {self.is_invited_sydney}\n"
            f"Is Invited [India]: {self.is_invited_india}\n"
            f"Is Coming [Sydney]: {self.is_coming_sydney}\n"
            f"Is Coming [India]: {self.is_coming_india}\n"
            f"Should Send Chinese Message: {self.chinese_message}\n"
            f"Contact Method: {self.preferred_contact_method}\n"
            f"Email: {self.email}\n"
            f"WhatsApp: {self.whatsapp}\n"
            f"Instagram: {self.instagram}\n"
            f"Messenger: {self.messenger}\n"
            f"Country: {self.country}\n"
            f"Invite Method: {self.invite_method}\n"
            f"Update Method: {self.update_method}\n"
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

    def get_friendly_names(self) -> str:
        total_guests = len(self._guests)
        guest_names = [
            self._guests[i].friendly_name
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


def str_cleanse(input_str: Any, remove_spaces=False):
    if input_str == "None" or input_str is None:
        return ""
    if remove_spaces:
        return str(input_str).replace(" ", "")
    return str(input_str)
