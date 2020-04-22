from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from . import models


@receiver(post_save, sender=User)
def account_profile(instance=None, created=None, **kwargs):
    if created:
        models.Profile.objects.create(user=instance)
    else:
        profile = models.Profile.objects.filter(user=instance)
        if not profile.count():
            models.Profile.objects.create(user=instance)

    instance.profile.save()


# Delete avatar if remove User
@receiver(post_delete, sender=models.Profile)
def profile_delete_avatar(sender, instance, **kwargs):
    instance.avatar.delete(False)
