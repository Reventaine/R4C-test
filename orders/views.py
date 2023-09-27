from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

from .models import Order


@receiver(post_save, sender=Order)
def send_email(sender, instance, **kwargs):
    model = instance.robot_serial[:2]
    version = instance.robot_serial[3:]

    subject = "Робот доступен в наличии"
    message = f"Добрый день!\n\nНедавно вы интересовались нашим роботом модели {model}" \
              f", версии {version}. Этот робот теперь в наличии. Если вам подходит этот вариант " \
              f"- пожалуйста, свяжитесь с нами. "

    recipient_list = [instance.customer.email]
    send_mail(subject, message, None, recipient_list)
