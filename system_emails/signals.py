from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import EmailType

@receiver(post_migrate)
def create_default_roles(sender, **kwargs):

    if sender.name == 'system_emails':
        default_roles = ['Administrator and user','User']


        for role in default_roles:
            EmailType.objects.get_or_create(name=role, is_active=True)