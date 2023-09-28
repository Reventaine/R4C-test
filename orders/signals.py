from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

from .models import Order
from robots.models import Robot


# Change availability for a robot that matches existing order and respectively closes the order
@receiver(post_save, sender=Robot)
def update_robot_availability(sender, instance, created, **kwargs):
    if created:
        robot_serial = instance.serial

        # Check if there are any orders with this serial and completed=False
        matching_orders = Order.objects.filter(robot_serial=robot_serial, completed=False)

        if matching_orders:
            instance.available = False
            instance.save()

            # Set completed=True for the first matching order and save it
            matching_order = matching_orders.first()
            matching_order.completed = True
            matching_order.save()


@receiver(post_save, sender=Order)
def send_email(sender, instance, **kwargs):
    if not instance.email_sent:
        # Check if there is a new corresponding robot
        matching_robot = Robot.objects.filter(serial=instance.robot_serial, available=True).first()

        # Email data to send
        model = instance.robot_serial[:2]
        version = instance.robot_serial[3:]
        subject = "Робот доступен в наличии"
        message = f"Добрый день!\n\nНедавно вы интересовались нашим роботом модели {model}" \
                  f", версии {version}. Этот робот теперь в наличии. Если вам подходит этот вариант " \
                  f"- пожалуйста, свяжитесь с нами. "
        recipient_list = [instance.customer.email]

        if instance.completed:
            # Send email and mark
            send_mail(subject, message, None, recipient_list)
            instance.email_sent = True
            instance.save()

        elif matching_robot:
            # Send email and mark, update robot and order statuses
            send_mail(subject, message, None, recipient_list)

            instance.completed = True
            instance.email_sent = True
            instance.save()

            matching_robot.available = False
            matching_robot.save()

