
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_email_task_done(email):
    send_mail('ToDo App', 'Your Task Completed successfully', 'rakhatrameyev@yandex.ru', [email])
    return None
def send_email_task_not_done(email):
    send_mail('ToDo App', 'Your Task not done', 'rakhatrameyev@yandex.ru', [email])
    return None



