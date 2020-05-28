from app import app
from flask_mail import Mail, Message
from smtplib import SMTPException, SMTPAuthenticationError, SMTPServerDisconnected

DEBUG = True

app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.zoho.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'support@repusight.com',
    MAIL_PASSWORD = 'repusight',
    DEFAULT_MAIL_SENDER='support@repusight.com'

))

mail = Mail(app)


def send_mail(recipients, eSubject, eBody):

    msg = Message(eSubject, sender="support@repusight.com", recipients=recipients, body=eBody)

    mail.send(msg)


def send_pdf_mail(attachment, pdf_name, recipients, cc, name, subject=None):
    body = 'Periodic analysis for {}'.format(name)

    try:
        if subject is None:
            msg = Message(recipients=recipients, cc=cc, sender='support@repusight.com', body=body)
            msg.attach(pdf_name + '.pdf', "application/pdf", attachment)
            mail.send(msg)
        else:
            msg = Message(recipients=recipients, cc=cc, subject=subject, body=body, sender='support@repusight.com')
            msg.attach(pdf_name + '.pdf', "application/pdf", attachment)
            mail.send(msg)
            return {'status': 'success'}
    except SMTPServerDisconnected:
        app.logger.error('ERROR: Server Disconnected')
        return {'status': 3}
    except SMTPException:
        app.logger.error('ERROR:Smtp exception')
        return {'status': 1}
    except SMTPAuthenticationError:
        app.logger.error('ERROR:Authentication Error')
        return {'status': 2}