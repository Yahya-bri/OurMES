from django.core.mail import send_mail
from django.conf import settings

def send_order_confirmation_email(order):
    subject = f"Order Confirmation - {order.id}"
    message = f"Thank you for your order!\n\nOrder ID: {order.id}\nTotal: {order.total}\n\nWe appreciate your business."
    recipient_list = [order.customer.email]

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

def send_delivery_notification_email(order):
    subject = f"Delivery Notification - Order {order.id}"
    message = f"Your order {order.id} has been dispatched and is on its way!\n\nTotal: {order.total}"
    recipient_list = [order.customer.email]

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

def send_password_reset_email(user):
    subject = "Password Reset Request"
    message = f"Hi {user.username},\n\nYou requested a password reset. Click the link below to reset your password:\n\n{settings.FRONTEND_URL}/reset-password?token={user.reset_token}"
    recipient_list = [user.email]

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)