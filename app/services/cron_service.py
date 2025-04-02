from app.models.email_model import MailStatus
from app.services.database_service import db_service
from app.services.email_service import send_email
from app.utils.util import logger

SENT = MailStatus.SENT.value
FAILED = MailStatus.FAILED.value


def should_send_email():
    records = db_service.get_record()
    if len(records) == 0:
        logger.debug("no mail to send")
        return
    else:
        for mailbox_id, record in records.items():
            send_result = send_email(record)
            send_status = send_result["send_status"]
            sender = send_result["sender"]

            db_service.update_record(
                mailbox_id, SENT if send_status is True else FAILED, sender
            )
            if send_status is True:
                logger.info(
                    f"send mail success, mailbox_id: {mailbox_id}, sender: {sender}"
                )
            else:
                logger.warning(
                    f"send mail failed, mailbox_id: {mailbox_id}, sender: {sender}"
                )


if __name__ == "__main__":
    should_send_email()
    pass
