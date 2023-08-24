from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import EmailType

@receiver(post_migrate)
def create_default_etype(sender, **kwargs):

    if sender.name == 'system_emails':
        default_etype = ['Administrator and user','User']


        for type in default_etype:
            EmailType.objects.get_or_create(name=type, is_active=True)