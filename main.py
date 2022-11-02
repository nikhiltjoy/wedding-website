from pathlib import Path
from dotenv import dotenv_values

from outreach.message.EmailMessageClient import EmailMessageClient
from outreach.message.MessengerMessageClient import MessengerMessageClient
from outreach.models.wedding_party import WeddingParty

if __name__ == "__main__":
    config = dotenv_values()
    wedding_props = {
        "sydney": {
            "date": "Saturday, October 7th 2023",
            "friendly_name": "Sydney, Australia",
            "participants": "Joanne and Nikhil",
        },
        "india": {
            "date": "Sunday, October 15th 2023",
            "friendly_name": "Kochi, Kerala, India",
            "participants": "Nikhil and Joanne",
        },
    }
    wedding_party = WeddingParty(
        input_csv_path=Path(config.get("GUEST_CSV_PATH")),
        save_the_date_filepaths=[
            Path(x) for x in config.get("SAVE_THE_DATE_PATHS").split(",")
        ],
        wedding_props=wedding_props
    )
    email_client = EmailMessageClient(
        sender_email=config.get("SENDER_EMAIL"),
        sender_pw=config.get("SENDER_EMAIL_PW")
    )
    messenger_client = MessengerMessageClient(
        bot_token=config.get("MESSENGER_PAGE_TOKEN")
    )
    party = wedding_party.get_party(3)
    guest = wedding_party.get_guest(6)
    # wedding_party.send_save_the_date_email(
    #     email_client=email_client,
    #     party=wedding_party.get_party(3)
    # )
    wedding_party.send_save_the_date_messenger(
        messenger_client=messenger_client,
        party=party
    )
    # send_test_msg_to_group_id("B86O6gowyaoB9INZmB9mqL")
    # send_test_msg(guest_df, 34)
    # for img in invite_images:
    #     send_image_to_userid(guest_df, 6, img)
