from django.contrib.auth.models import Group
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_groups(sender, **kwargs):
    if sender.name == "cybercafe":  # remplace par le nom de ton app
        Group.objects.get_or_create(name="admin")
        Group.objects.get_or_create(name="user")

        