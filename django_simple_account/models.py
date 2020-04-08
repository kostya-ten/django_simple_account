import re
from os import urandom
from pathlib import Path

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import validators


class Profile(models.Model):
    GENDER = (
        (1, _('Male')),
        (2, _('Female')),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("User")
    )

    gender = models.SmallIntegerField(
        choices=GENDER,
        null=True,
        blank=True,
        verbose_name=_("Gender")
    )

    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Birth date")
    )

    phone = models.BigIntegerField(
        null=True,
        blank=True,
        validators=[validators.mobile_number],
        verbose_name=_("Mobile phone"),
    )

    def path(self, filename):
        extension = Path(filename).suffix
        key = urandom(16).hex()
        result = re.match(r'([a-z0-9]{2})([a-z0-9]{2})', key)
        return 'avatar/{0}/{1}/{2}'.format(result.group(1), result.group(2), key + extension)

    avatar = models.ImageField(upload_to=path, null=True, blank=True)

    def __str__(self):
        return 'User profile {user}'.format(user=self.user)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")


class OAuth(models.Model):
    PROVIDER = (
        (1, 'Google'),
        (2, 'Facebook'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    oauth_id = models.CharField(max_length=255, verbose_name=_("OAuth ID"))
    provider = models.IntegerField(choices=PROVIDER, verbose_name=_("Server"))

    class Meta:
        unique_together = (('oauth_id', 'provider'),)
        verbose_name = _("OAuth")
        verbose_name_plural = _("OAuth")

