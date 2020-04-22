import re

import phonenumbers
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from email_validator import validate_email, EmailNotValidError
from phonenumbers import PhoneNumber
from phonenumbers.phonenumberutil import number_type, PhoneNumberType


def username(name: str) -> str:
    """
    Checks the validity of an username.
    :param name: User name сhecked.
    :returns: name
    :raise: ValidationError If the username is not a regular expression ^[a-z]+[a-z0-9]+[_-]?[a-z0-9]+$
    """
    name = name.lower().strip()
    match = re.search(r'^[a-z]+[a-z0-9]+[_-]?[a-z0-9]+$', name)
    if match:
        return name
    else:
        raise ValidationError(_("Enter a valid username. \
This value may contain only English letters, numbers, and _ - characters. \
Username should not begin with a number."))


def username_dublicate(name: str) -> str:
    """
    Checks the dublicate an username.
    :param name: User name сhecked.
    :returns: name
    :raise: ValidationError If the username is dublicate
    """

    name = name.lower().strip()

    user = User.objects.filter(username=name)
    if user.count():
        raise ValidationError(_("A user with that username already exists"))

    return name


def mobile_number(number: int) -> PhoneNumber:
    """
    Checks the validity of a mobile phone number.
    :param number: mobile phone number.
    :returns: number
    :raise: ValidationError If the mobile phone number is not valid
    """

    match = re.search(r'^[0-9]+$', str(number))
    if not match:
        raise ValidationError(_("Invalid mobile phone number"))

    number = "+{number}".format(number=number)
    number = phonenumbers.parse(number)

    if not number_type(number) == PhoneNumberType.MOBILE:
        raise ValidationError(_('Invalid mobile phone number'))
    else:
        return number


def email(val: str) -> str:
    """
    Checks the validity syntax of an email
    :param val:
    :returns: email
    :raise: ValidationError If the incorrect email address
    """
    val = val.lower().strip()

    user = val.rsplit('@', 1)[0]
    domain = val.rsplit('@', 1)[-1]

    if domain in ['ya.ru', 'yandex.by', 'yandex.com', 'yandex.kz', 'yandex.ua']:
        val = user + '@yandex.ru'

    try:
        validate_email(val)
    except EmailNotValidError:
        raise ValidationError(_("Enter a valid email address"))
    return val


def email_blacklist(val: str) -> str:
    """
    Checks the blacklist db an email
    :param val: email address
    :returns: email
    :raise: ValidationError If the email address is blacklist db
    """
    val = val.lower().strip()
    domain = val.rsplit('@', 1)[-1]
    if domain in [
        'for4mail.com',
        '2mailnext.com',
        'prmail.top',
        'youmails.online',
        'proto2mail.com',
        'mail-2-you.com',
        'reddcoin2.com',
        'for4mail.com',
        '2mailnext.top',
        'jo-mail.com',
        'mailapps.online',
        'plutocow.com',
        'ezehe.com',
        'sharklasers.com',
        'guerrillamail.info',
        'grr.la',
        'guerrillamail.biz',
        'guerrillamail.com',
        'guerrillamail.de',
        'guerrillamail.net',
        'guerrillamail.org',
        'guerrillamailblock.com',
        'pokemail.net',
        'spam4.me',
        'fosil.pro',
        'socrazy.club',
        'getamailbox.org',
        'ourawesome.life',
        'mailboxonline.org',
        'careless-whisper.com',
        'ourawesome.life',
        'ourawesome.online',
        'secure-box.info',
        'secure-box.online',
        'socrazy.club',
        'socrazy.online',
        'yevme.com',
        'trashmail.com',
        '0box.eu',
        'contbay.com',
        'damnthespam.com',
        'kurzepost.de',
        'objectmail.com',
        'proxymail.eu',
        'rcpt.at',
        'trash-mail.at',
        'trashmail.at',
        'trashmail.com',
        'trashmail.io',
        'trashmail.me',
        'trashmail.net',
        'wegwerfmail.de',
        'wegwerfmail.net',
        'wegwerfmail.org',
    ]:
        raise ValidationError(_("Email address cannot be registered!"))
    return val


def email_dublicate(val: str) -> str:
    """
    Checks the dublicate an email
    :param val: email address
    :returns: email
    :raise: ValidationError If the email address is dublicate
    """
    val = val.lower().strip()

    user = val.rsplit('@', 1)[0]
    domain = val.rsplit('@', 1)[-1]
    if domain in ['ya.ru', 'yandex.by', 'yandex.com', 'yandex.kz', 'yandex.ua']:
        val = user+'@yandex.ru'

    if User.objects.filter(email=val).exists():
        raise ValidationError(_("User with this email is already exists."))
    return val


def password(val: str) -> str:
    """
    Checks the password syntax
    :param val: password
    :returns: password
    :raise: ValidationError If the password is not correct
    """
    match = re.search(r'^[a-z0-9`@#$%^&*()_=+\[\]{};:"\\|.,]+$', val, re.IGNORECASE)
    if not match:
        err = _('For the password, you can use only Latin letters, numbers, and symbols')
        raise ValidationError(err)

    return val
