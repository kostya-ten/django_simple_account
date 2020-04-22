import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import django_simple_account.models
import django_simple_account.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '__latest__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    )
                ),
                (
                    'gender',
                    models.SmallIntegerField(
                        blank=True,
                        choices=[
                            (1, 'Male'),
                            (2, 'Female'),
                        ],
                        null=True,
                        verbose_name='Gender',
                    )
                ),
                (
                    'birth_date',
                    models.DateField(
                        blank=True,
                        null=True,
                        verbose_name='Birth date',
                    )
                ),
                (
                    'phone',
                    models.BigIntegerField(
                        blank=True,
                        null=True,
                        validators=[django_simple_account.validators.mobile_number],
                        verbose_name='Mobile phone',
                    )
                ),
                (
                    'avatar',
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=django_simple_account.models.unique_file_path_avatar,
                    )
                ),
                (
                    'user',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='User',
                    )
                ),
            ],
            options={'verbose_name': 'Profile', 'verbose_name_plural': 'Profiles'}
        ),
        migrations.CreateModel(
            name='OAuth',
            fields=[
                (
                    'id',
                    models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
                ),
                (
                    'oauth_id',
                    models.CharField(max_length=255, verbose_name='OAuth ID')
                ),
                (
                    'provider',
                    models.IntegerField(choices=[(1, 'Google'), (2, 'Facebook')], verbose_name='Server')
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='User'
                    )
                ),
            ],
            options={
                'verbose_name': 'OAuth',
                'verbose_name_plural': 'OAuth',
                'unique_together': {('oauth_id', 'provider')},
            },
        ),
    ]
