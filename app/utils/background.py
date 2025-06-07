from fastapi import BackgroundTasks
import smtplib
from email.message import EmailMessage

def run_background_tasks(background_tasks: BackgroundTasks, data: dict):
    background_tasks.add_task(send_email_notification, data)

def send_email_notification(data: dict):
    msg = EmailMessage()
    msg.set_content(f"Background Event Triggered: {data}")
    msg["Subject"] = f"DTech Event: {data.get('event')}"
    msg["From"] = "noreply@dtech.com"
    msg["To"] = "admin@dtech.com"

    try:
        with smtplib.SMTP("localhost") as smtp:
            smtp.send_message(msg)
    except Exception as e:
        print("Email error:", e)
