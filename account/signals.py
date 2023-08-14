from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import UserRole

@receiver(post_migrate)
def create_default_roles(sender, **kwargs):

    if sender.name == 'account':
        default_roles = ['site_admin','holding_admin','company_admin','user']


        for role in default_roles:
            UserRole.objects.get_or_create(name=role, is_deleted=False)