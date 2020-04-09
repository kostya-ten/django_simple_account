import base64
import hashlib
import hmac
import json
import logging
import os
from importlib import import_module

import requests
from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from oauth2client import client

from . import forms, converters, models

logger = logging.getLogger(__name__)


class Login(generic.FormView):
    form_class = forms.Login
    template_name = "django_simple_account/login.html"
    success_url = '/'

    def get_success_url(self):
        if self.request.GET.get('next'):
            logger.debug("next redirect {next}".format(next=self.request.GET.get('next')))
            return self.request.GET.get('next')
        else:
            logger.debug("next redirect {next}".format(next=self.success_url))
            return self.success_url

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response


class Signup(generic.FormView):
    form_class = forms.Signup
    template_name = "django_simple_account/signup.html"
    success_url = settings.LOGIN_URL

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response

    def form_valid(self, form):
        response = super().form_valid(form)
        form.confirmation(request=self.request)
        return response


class ConfirmationEmail(generic.View):
    form_class = forms.Signup

    def get(self, request, session: converters.ConfirmationEmailSession, *args, **kwargs):
        data = {}
        for item in ['username', 'last_name', 'first_name', 'email', 'password1', 'password2']:
            data[item] = getattr(session, item)
        form = self.form_class(data=data)

        if not form.is_valid():
            messages.error(self.request, _("The link in the email confirmation email is out of date"))
            return redirect(settings.LOGIN_URL)

        if session.action != 'signup':
            messages.error(self.request, _("The link in the email confirmation email is out of date"))
            return redirect(settings.LOGIN_URL)

        user = form.save()
        session.session.delete()
        auth.login(self.request, user)
        messages.success(self.request, _("Your address has been successfully verified"))
        return redirect(session.next)


class OAuthFacebook(generic.FormView):
    form_class = forms.OAuthFacebook
    success_url = '/'
    template_name = 'django_simple_account/oauth_facebook.html'

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response

    def form_valid(self, form):
        access_token = form.cleaned_data.get('access_token')
        params = {
            'fields': 'id,last_name,first_name,picture.width(100).height(100){url,height,width},email',
            'access_token': access_token,
        }
        response = requests.get('https://graph.facebook.com/v6.0/me', params=params)
        if response.status_code == 200:
            j = response.json()

            session_store = import_module(settings.SESSION_ENGINE).SessionStore
            session = session_store()
            session.set_expiry(60 * 60 * 3)

            session['oauth_id'] = j.get('id')
            session['last_name'] = j.get('last_name')
            session['first_name'] = j.get('first_name')
            session['provider'] = 2
            session['email'] = None
            session['username'] = None
            session['avatar'] = None

            if j.get('picture') and j.get('picture').get('data') and j.get('picture').get('data').get('url'):
                session['avatar'] = j.get('picture').get('data').get('url')

            email = j.get('email')
            if j.get('email'):
                email = email.strip().lower()
                user = email.rsplit('@', 1)[0]
                user = str(user).replace(".", "_")

                session['email'] = email
                session['username'] = user

            session.create()
            return JsonResponse({'session': session.session_key})


class OAuthGoogle(generic.FormView):
    form_class = forms.OAuthGoogle
    success_url = '/'
    template_name = 'django_simple_account/oauth_google.html'

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response

    def form_valid(self, form):
        credentials = client.credentials_from_code(
            client_id=getattr(settings, 'OAUTH_GOOGLE_CLIENT_ID', os.environ.get('OAUTH_GOOGLE_CLIENT_ID')),
            client_secret=getattr(settings, 'OAUTH_GOOGLE_SECRET_KEY', os.environ.get('OAUTH_GOOGLE_SECRET_KEY')),
            code=form.cleaned_data.get('code'),
            scope='https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile'
        )

        email = credentials.id_token.get('email')
        email = email.strip().lower()
        user = email.rsplit('@', 1)[0]
        user = str(user).replace(".", "_")

        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        session = session_store()
        session.set_expiry(60 * 60 * 3)

        session['oauth_id'] = credentials.client_id
        session['username'] = user
        session['email'] = None
        session['first_name'] = credentials.id_token.get('given_name')
        session['last_name'] = credentials.id_token.get('family_name')
        session['avatar'] = credentials.id_token.get('picture')
        session['provider'] = 1

        if credentials.id_token.get('email_verified'):
            session['email'] = email

        session.create()
        return JsonResponse({'session': session.session_key})


class OAuthCompletion(generic.FormView):
    form_class = forms.OAuthCompletion
    success_url = '/'
    template_name = 'django_simple_account/oauth_completion.html'

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response

    def get_success_url(self):
        if self.request.GET.get('next'):
            return self.request.GET.get('next')
        else:
            return self.success_url

    def get(self, request, session: converters.OAuthSession, *args, **kwargs):

        oauth = models.OAuth.objects.filter(oauth_id=session.oauth_id, provider=session.provider)[:1]
        if oauth.exists():
            user = oauth.get().user
            self.download_avatar(session=session, user=user)

            auth.login(self.request, user)
            session.session.delete()
            return redirect(self.get_success_url())

        if session.email:
            user = User.objects.filter(email=session.email)[:1]
            if user.exists():
                user = user.get()
                self.download_avatar(session=session, user=user)

                auth.login(self.request, user)
                models.OAuth.objects.create(oauth_id=session.oauth_id, provider=session.provider, user=user)
                session.session.delete()
                return redirect(self.get_success_url())

        return super().get(request)

    def form_valid(self, form):
        session = self.kwargs.get('session')
        user = form.save(session=session)
        self.download_avatar(session=session, user=user)
        session.session.delete()
        auth.login(self.request, user)
        response = super().form_valid(form)
        return response

    @staticmethod
    def download_avatar(session: converters.OAuthSession, user: User):
        if not session.avatar:
            return None

        response = requests.get(url=session.avatar)
        if response.status_code != 200:
            return None

        profile = get_object_or_404(models.Profile, user=user)
        if not profile.avatar:
            profile.avatar.save('avatar.jpg', ContentFile(response.content))


@method_decorator(csrf_exempt, name='dispatch')
class FacebookDeactivate(generic.FormView):
    form_class = forms.FacebookDeactivate
    template_name = 'django_simple_account/blank.html'
    success_url = '/'

    @staticmethod
    def base64_url_decode(inp):
        padding_factor = (4 - len(inp) % 4) % 4
        inp += "=" * padding_factor
        return base64.b64decode(inp.translate(dict(zip(map(ord, u'-_'), u'+/'))))

    def parse_signed_request(self, signed_request=None):
        secret = settings.OAUTH_FACEBOOK_SECRET_KEY

        line = signed_request.split('.', 2)
        encoded_sig = line[0]
        payload = line[1]

        sig = self.base64_url_decode(inp=encoded_sig)
        data = json.loads(self.base64_url_decode(payload))

        if data.get('algorithm').upper() != 'HMAC-SHA256':
            return None
        else:
            expected_sig = hmac.new(secret.encode(), msg=payload.encode(), digestmod=hashlib.sha256).digest()
            if sig == expected_sig:
                return data

    def form_valid(self, form):
        result = self.parse_signed_request(signed_request=form.cleaned_data.get('signed_request'))
        if result.get('user_id'):
            models.OAuth.objects.filter(oauth_id=result.get('user_id'), provider=2).delete()
            logger.info("Delete OAuth user by facebook deactivate oauth_id:{oauth_id}".format(
                oauth_id=result.get('user_id'))
            )
        return super().form_valid(form)
