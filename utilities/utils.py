import requests
from django.conf import settings
from django.core.mail import send_mail
from django.db import connections
from django.db.migrations.executor import MigrationExecutor
from django.template import loader


def is_database_synchronized():
    connection = connections['default']
    connection.prepare_database()
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    return not executor.migration_plan(targets)


def modify_fields(**kwargs):
    def wrap(cls):
        for field, prop_dict in kwargs.items():
            for prop, val in prop_dict.items():
                setattr(cls._meta.get_field(field), prop, val)
        return cls

    return wrap


def send_mail_using_templates(subject_string, email_template_name,
                              context, to_email):
    """
    :param subject_string: this should be a string which can be formatted using subject_string.format(**context)
    :param email_template_name: django template path which will be rendered using context
    :param context: dict
    :param to_email: single email or a list of emails
    :return:
    """

    if type(to_email) != list:
        to_email = [to_email]

    subject = subject_string.format(**context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = loader.render_to_string(email_template_name, context)
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, to_email, html_message=body)


def send_message(sms_to, sms_body):
    r = requests.post(
        "https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json".format(sid=settings.TWILIO_ACCOUNT_SID),
        auth=(settings.TWILIO_KEY, settings.TWILIO_AUTH_TOKEN),
        data={
            'From': settings.TWILIO_SMS_FROM,
            'To': sms_to,
            'Body': sms_body
        })
