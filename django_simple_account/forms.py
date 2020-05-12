import logging
from email.utils import make_msgid
from importlib import import_module

from django import forms
from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from . import models, converters, validators

logger = logging.getLogger(__name__)


class BaseForm(forms.Form):
    """ Base class for forms in this project """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            if isinstance(self.fields[field].widget, forms.widgets.ClearableFileInput):
                self.fields[field].widget.attrs.update({'class': 'form-control custom-file-input'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-control'})


class Login(AuthenticationForm, BaseForm):
    pass


class Signup(UserCreationForm, BaseForm):
    username = forms.CharField(label=_('Username'), validators=(validators.username, validators.username_dublicate))
    first_name = forms.CharField(label=_('First name'))
    last_name = forms.CharField(label=_('Last name'))
    email = forms.EmailField(
        label=_('Email'),
        validators=(validators.email, validators.email_blacklist, validators.email_dublicate)
    )

    password1 = forms.CharField(
        label=_('Password'),
        validators=(validators.password,),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )

    password2 = forms.CharField(
        label=_('Password confirmation'),
        validators=(validators.password,),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )

    def confirmation(self, request: WSGIRequest = None) -> import_module(settings.SESSION_ENGINE).SessionStore:
        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        session = session_store()
        session.set_expiry(60 * 60 * 24)
        session['action'] = 'signup'

        for key, val in self.cleaned_data.items():
            session[key] = val

        if hasattr(request, 'GET'):
            session['next'] = request.GET.get('next', '/')
            session['params'] = request.GET.dict()
        else:
            session['next'] = '/'
            session['params'] = {}

        session.create()

        subject = render_to_string('django_simple_account/email/signup.subject.txt', {}).strip()
        body = render_to_string('django_simple_account/email/signup.body.html', {
            'request': request,
            'session_key': session.session_key,
        })

        msg = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[self.cleaned_data.get('email')],
            headers={'Message-ID': make_msgid(domain=request.get_host())}
        )
        msg.content_subtype = "html"
        msg.send()

        logger.info("send confirmation email to:{to}, session:{session}, message-id:{message_id}".format(
            to=msg.to,
            session=session.session_key,
            message_id=msg.extra_headers.get('Message-ID'),
        ))
        return session

    class Meta:
        """ Meta class """
        model = User
        fields = ('username', 'last_name', 'first_name', 'email', 'password1', 'password2')


class OAuthGoogle(BaseForm):
    code = forms.CharField(label=_('Code'), widget=forms.TextInput())


class OAuthFacebook(BaseForm):
    access_token = forms.CharField(label=_('Access Token'), widget=forms.TextInput())


class OAuthCompletion(BaseForm):
    username = forms.CharField(
        label=_('Username'),
        widget=forms.TextInput(),
        validators=(validators.username, validators.username_dublicate)
    )

    def save(self, session: converters.OAuthSession):
        username = self.cleaned_data.get('username')
        user = User.objects.create_user(
           username=username,
           first_name=session.first_name,
           last_name=session.last_name,
           email=session.email,
        )
        models.OAuth.objects.create(oauth_id=session.oauth_id, provider=session.provider, user=user)
        return user


class FacebookDeactivate(BaseForm):
    signed_request = forms.CharField(label=_('signed_request'), widget=forms.TextInput())


class ForgotPassword(BaseForm):
    email = forms.EmailField(label=_('Email'), validators=(validators.email, validators.email_exist))

    def confirmation(self, request: WSGIRequest = None) -> import_module(settings.SESSION_ENGINE).SessionStore:
        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        session = session_store()
        session.set_expiry(60 * 60 * 24)
        session['action'] = 'forgotpassword'

        for key, val in self.cleaned_data.items():
            session[key] = val

        session.create()

        subject = render_to_string('django_simple_account/email/forgotpassword.subject.txt', {}).strip()
        body_html = render_to_string('django_simple_account/email/forgotpassword.body.html', {
            'request': request,
            'session_key': session.session_key,
        })

        body_text = render_to_string('django_simple_account/email/forgotpassword.body.txt', {
            'request': request,
            'session_key': session.session_key,
        })

        msg = EmailMultiAlternatives(
            body=body_text,
            subject=subject,
            to=[self.cleaned_data.get('email')],
            headers={'Message-ID': make_msgid(domain=request.get_host())}
        )
        msg.attach_alternative(body_html, "text/html")
        msg.send()

        return session


class ForgotPasswordConfirmation(BaseForm):
    password1 = forms.CharField(
        label=_("New password"),
        validators=(validators.password,),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )

    password2 = forms.CharField(
        label=_("New password confirmation"),
        validators=(validators.password,),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )

    error_messages = {
        'password_mismatch': _('The two password fields didn’t match.'),
    }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('initial').get('user')
        super().__init__(*args, **kwargs)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(self.error_messages.get('password_mismatch'), code='password_mismatch')

        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data.get("password1")
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
