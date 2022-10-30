import os
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Mail:
    def __init__(self):
        self.recipients = os.getenv('EMAIL_RECIPIENTS').split(',')
        self.sender_email = "administradores@img.com.br"
        self.password = os.getenv('EMAIL_PASSWORD')
        self.server = "smtp.office365.com"

    def _build_message(self, text, html, subject):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.sender_email
        message["To"] = ', '.join(self.recipients)

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        message.attach(part1)
        message.attach(part2)

        return message
    
    def send(self, text, html, subject):
        message = self._build_message(text, html, subject)

        context = ssl.create_default_context()
        with smtplib.SMTP(self.server, 587) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, self.recipients, message.as_string())