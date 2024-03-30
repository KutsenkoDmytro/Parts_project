from django.template import context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage

from parts_project.settings import FROM_EMAIL, EMAIL_ADMIN
from system_emails.models import EmailSendingFact
from django.forms.models import model_to_dict
from orders.models import OrderItem
from django.db.models import ExpressionWrapper, DecimalField, F

class SendingEmail(object):
    from_email = 'PartsProject <%s>' % FROM_EMAIL
    target_emails = []
    bcc_emails = [] #

    # def__init__(self,data):
    #   data = data
    #   self.data = data
    #   self.orders = data.get('order')

    def sending_email(self, type_id, email=None, order=None):
        # if not email, so far is type_id==1 which is admin notification
        #if not email:
        #    email = EMAIL_ADMIN

        reply_to_emails = ['damhp@astra-group.ua'] # Reset the list every time the sending_email method is called.

        target_emails = [email, EMAIL_ADMIN]
        if order.email:
            reply_to_emails.append(order.email)

        vars = {
        }

        if type_id == 1:  # admin notification
            subject = 'New order'
            vars['order_fields'] = model_to_dict(
                order)  # model_to_dict (instance, fields=[], exclude=[])
            vars['order'] = order
            products_in_order = OrderItem.objects.filter(
                order_id=order.id)

            vars['products_in_order'] = products_in_order

            message = get_template(
                'order_notification_admin.html').render(
                vars)

        elif type_id == 2: # customer notification
            subject = 'Your order has been received!'
            message = get_template('order_notification_customer.html').render(
                vars)

        msg = EmailMessage(
            subject, message, from_email=self.from_email, to=target_emails,
            bcc=self.bcc_emails, reply_to=reply_to_emails)

        msg.content_subtype = 'html'
        msg.mixed_subtype = 'related'

        msg.send()

        kwards = {
            'type_id': type_id,
            'email': email
        }

        if order:
            kwards['order'] = order
        EmailSendingFact.objects.create(**kwards)

        print('Email was sent successfuly')