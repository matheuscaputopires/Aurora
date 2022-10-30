from unittest import TestCase
from mock import patch, MagicMock

import os

from mock.mock import ANY
from helper.mail import Mail

class TestMail(TestCase):

    #https://expobrain.net/2013/08/27/mocking-objects-in-unit-tests/
    @patch("helper.mail.smtplib.SMTP")
    def test_send_email_with_decorator(self, mock_smtp):
        
        recipients = 'test1@gmail.com,test2@gmail.com'

        os.environ['EMAIL_RECIPIENTS'] = recipients
        os.environ['EMAIL_PASSWORD'] = 'a123'

        mail = Mail()        

        text = "Hello"
        html = "<html><body>Hello</body></html>"
        subject = "Test send email"
        mail.send(text, html, subject)

        to = recipients.split(',')
        sender_email = "administradores@img.com.br"
        
        mock_smtp.return_value.__enter__().sendmail.assert_called_once_with(sender_email, to, ANY)

