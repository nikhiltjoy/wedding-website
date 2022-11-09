from pathlib import Path
from dotenv import dotenv_values

from outreach.data.repository.google_sheets import GSheetClient
from outreach.message.EmailMessageClient import EmailMessageClient
from outreach.message.MessengerMessageClient import MessengerMessageClient
from outreach.message_sender import MessageSender
from outreach.models.wedding_party import WeddingParty

if __name__ == "__main__":
    config = dotenv_values()
    gc = GSheetClient(Path(config.get("CREDS_PATH")))
    wedding_party = WeddingParty(gc, config.get("SHEET_ID"))
    data_dir = Path(config.get("DATA_PATH"))
    email_client = EmailMessageClient(
        sender_email=config.get("SENDER_EMAIL"),
        sender_pw=config.get("SENDER_EMAIL_PW")
    )
    messenger_client = MessengerMessageClient(
        bot_token=config.get("MESSENGER_PAGE_TOKEN")
    )
    message_sender = MessageSender(
        data_dir=data_dir,
        email_client=email_client
    )

    parties_to_invite = [3]  # wedding_party.get_parties_with_emails()
    local_db_dir = data_dir / "guests_db.parquet"
    for p in parties_to_invite:
        message_sender.send_save_the_date_email(party=wedding_party.get_party(p))
        wedding_party.persist_local(local_db_dir)
    wedding_party.persist()
    # wedding_party.send_save_the_date_messenger(
    #     messenger_client=messenger_client,
    #     party=party
    # )
    # send_test_msg_to_group_id("B86O6gowyaoB9INZmB9mqL")
    # send_test_msg(guest_df, 34)
    # for img in invite_images:
    #     send_image_to_userid(guest_df, 6, img)
