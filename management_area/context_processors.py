from .models import PrivacyPolicy, Documentation, Contact


def getting_privacy_policy(request):

    privacy_policy = PrivacyPolicy.objects.filter(is_active=True).last()
    return locals()


def getting_documentation(request):

    documentation = Documentation.objects.filter(is_active=True).last()
    return locals()

def getting_contact(request):

    contact = Contact.objects.filter(is_active=True).last()
    return locals()