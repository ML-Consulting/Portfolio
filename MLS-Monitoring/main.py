import smtplib
from email.message import EmailMessage
import logging

from config import config
from pubsub_notifications import replay_pubsub_messages


def send_log_alert(email, password, subject, body):


    """Sends a plain text email alert."""
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = email
    msg['To'] = email

    try:
        # Use a context manager to ensure the connection closes
        with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
            server.starttls(context=config.context) # Secure the connection
            server.login(email, password)
            server.send_message(msg)
        logging.info(f"Successfully sent email to {email}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

# --- Usage Example ---
def main():

    try:
        email, password = config.get_gmail_creds()
        messages = replay_pubsub_messages()
    except Exception as e:
        logging.error(f"Error retrieving credentials or messages: {e}")
        return

    try:
        if messages:    
            send_log_alert(
                    email=email,
                    password=password,
                    subject="Pub/Sub Log Alert >= WARNING",
                    body= str(messages)
                )
        else:
            logging.info("No messages to alert.")
            return
    except Exception as e:
        logging.error(f"Error in main function: {e}")

