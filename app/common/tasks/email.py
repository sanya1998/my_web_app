import smtplib
from email.message import EmailMessage

from app.config.main import settings
from app.resources.celery_ import celery


def create_booking_notify_template(
    booking: dict,
    email_to: str,
) -> EmailMessage:
    email = EmailMessage()
    email["Subject"] = "Успешное бронирование"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
        <h1>Успешное бронирование!</h1>
        Вы забронировали номер в отеле с {booking["date_from"]} по {booking["date_to"]}
        """,
        subtype="html",
    )
    return email


@celery.task
def send_booking_notify_email(booking: dict, email_to: str):
    email_to = settings.SMTP_USER  # TODO: remove this mock
    msg_content = create_booking_notify_template(booking, email_to)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg_content)
