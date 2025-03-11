import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import requests

from app.models.email_model import Email
from app.utils.util import Config, logger

send_freq = {}  # 发送频率初始化


def send_email(email: Email) -> dict[str, bool | Any]:
    config = Config()
    contact_lists = config.contact_lists
    mail_server = config.mail_server
    email_type = email.type.value
    mails = contact_lists[email_type]

    if len(mails) == 1:
        sender = mails[0]

    else:  # 发件负载均衡
        if email_type not in send_freq:
            send_freq[email_type] = {}
            for m in mails:
                send_freq[email_type][m] = 0

        min_freq_mail = min(send_freq[email_type], key=send_freq[email_type].get)
        sender = min_freq_mail
        send_freq[email_type][sender] += 1

    logger.debug(f"send_freq: {send_freq}")

    smtp_server = mail_server[sender]["host"]
    port = mail_server[sender]["port"]
    sender_email = mail_server[sender]["username"]
    password = mail_server[sender]["password"]

    message = MIMEMultipart("alternative")
    message["Subject"] = email.subject
    message["From"] = sender_email

    if "," in email.recipient:
        email.recipient = email.recipient.split(",")

    if isinstance(email.recipient, list):
        message["To"] = ", ".join(email.recipient)
    else:
        message["To"] = email.recipient

    part = MIMEText(email.body, "html")
    message.attach(part)

    send_status = True
    try:
        server = smtplib.SMTP_SSL(smtp_server, port)
        server.login(sender_email, password)

        server.sendmail(sender_email, email.recipient if isinstance(email.recipient, list) else [email.recipient], message.as_string())
        server.quit()
        logger.debug(message.__str__())
        logger.info(f"send mail success, recipient: {email.recipient}, sender: {sender_email}, subject: {email.subject}")
    except Exception as e:
        send_status = False
        logger.error(f"send mail failed, {e}, mail_info: {email.dict()}")

    callback_url = email.callback_on_success if send_status is True else email.callback_on_failure

    if callback_url is not None:
        try:
            requests.get(callback_url.__str__(), timeout=3)
        except Exception as e:
            logger.warning(f"callback failed, {callback_url}, {e}, mail_info: {email.dict()}")

    return {"send_status": send_status, "sender": sender_email}
