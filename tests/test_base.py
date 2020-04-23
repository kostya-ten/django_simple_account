import hashlib
import re
from importlib import import_module

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail
from django.core.exceptions import ValidationError
from django.test import TestCase, RequestFactory
from django.urls import reverse

from django_simple_account import validators, views, converters, models


class Validators(TestCase):

    def test_mobile_number(self):
        self.assertEqual(validators.mobile_number(79091600000).national_number, 9091600000)

        with self.assertRaises(ValidationError):
            validators.mobile_number(74950000000)

        with self.assertRaises(ValidationError):
            validators.mobile_number('abc')

    def test_email(self):

        # Invalid
        with self.assertRaises(ValidationError):
            validators.email('kazerogova')

        with self.assertRaises(ValidationError):
            validators.email('kazerogova@')

        with self.assertRaises(ValidationError):
            validators.email('kazerogova@exampleexampleexampleexampleexampleexample.com')

        with self.assertRaises(ValidationError):
            validators.email('kazerogova@example.abc')

        with self.assertRaises(ValidationError):
            validators.email('kaze@rogova@example.com')

        # Valid
        self.assertEqual(validators.email('kazerogova@example.com'), 'kazerogova@example.com')
        self.assertEqual(validators.email('Kazerogova@example.com'), 'kazerogova@example.com')
        self.assertEqual(validators.email('        kazerogova@example.com        '), 'kazerogova@example.com')
        self.assertEqual(validators.email('kazerogova@yandex.com'), 'kazerogova@yandex.ru')
        self.assertEqual(validators.email('kazerogova@yandex.kz'), 'kazerogova@yandex.ru')
        self.assertEqual(validators.email('kazerogova@ya.ru'), 'kazerogova@yandex.ru')

    def test_email_blacklist(self):
        with self.assertRaises(ValidationError):
            validators.email_blacklist('kazerogova@for4mail.com')

        self.assertEqual(validators.email('kazerogova@example.com'), 'kazerogova@example.com')

    def test_email_dublicate(self):
        User.objects.create_user(username='username', email="devnull@yandex.ru")
        with self.assertRaises(ValidationError):
            validators.email_dublicate('devnull@yandex.ru')

    def test_username_dublicate(self):
        User.objects.create_user(username='username', email="devnull@yandex.ru")

        with self.assertRaises(ValidationError):
            validators.username_dublicate(name='username')

        with self.assertRaises(ValidationError):
            validators.username_dublicate(name='    username        ')

        with self.assertRaises(ValidationError):
            validators.username_dublicate(name='    USERNAME        ')

        result = validators.username_dublicate(name='username-username')
        self.assertEqual(result, 'username-username')

    def test_username(self):
        with self.assertRaises(ValidationError):
            validators.username(name='1username')

        with self.assertRaises(ValidationError):
            validators.username(name='username-username-username')

        with self.assertRaises(ValidationError):
            validators.username(name='username-username_username')

        with self.assertRaises(ValidationError):
            validators.username(name='xn--username')

        result = validators.username(name='username')
        self.assertEqual(result, 'username')


class Login(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.pwd = hashlib.sha256(str('hello word').encode()).hexdigest()

    def test_login(self):
        request = self.factory.get(reverse('accounts-login'))
        response = views.Login.as_view()(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post(reverse('accounts-login'), data={'username': 'username', 'password': 'password'})
        response = views.Login.as_view()(request)
        response.render()

        self.assertInHTML(
            '<div class="alert alert-danger div-max-width" role="alert">'
            'Please enter a correct username and password. Note that both fields may be case-sensitive.'
            '</div>',
            response.content.decode()
        )
        self.assertEqual(response.status_code, 400)

    def test_login_valid(self):
        User.objects.create_user(username='username', password=self.pwd, email="devnull@yandex.ru")

        request = self.factory.post(reverse('accounts-login'), data={'username': 'username', 'password': self.pwd})
        response = views.Login.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_login_valid_next(self):
        User.objects.create_user(username='username', password=self.pwd, email="devnull@yandex.ru")

        data = {'username': 'username', 'password': self.pwd}
        request = self.factory.post(reverse('accounts-login') + "?next=/next/", data=data)
        response = views.Login.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/next/', fetch_redirect_response=False)


class Signup(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.pwd = hashlib.sha256(str('hello word').encode()).hexdigest()

    def test_signup(self):

        # Check request get
        request = self.factory.get(reverse('accounts-signup'))
        response = views.Signup.as_view()(request)
        self.assertEqual(response.status_code, 200)

        # Check request normal data
        request = self.factory.post(reverse('accounts-signup') + "?next=/next/", data={
            'username': 'test_user',
            'first_name': 'Лилу',
            'last_name': 'Казерогова',
            'email': 'devnull@yandex.ru',
            'password1': self.pwd,
            'password2': self.pwd,
        })

        response = views.Signup.as_view()(request)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body
        gp = re.search('confirmation/email/([a-z0-9]+)/', body)
        self.assertRegex(gp.group(1), '^[a-z0-9]+$')

        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        session = session_store(session_key=gp.group(1))

        self.assertEqual(session.get('username'), 'test_user')
        self.assertEqual(session.get('password1'), self.pwd)
        self.assertEqual(session.get('password2'), self.pwd)
        self.assertEqual(session.get('last_name'), 'Казерогова')
        self.assertEqual(session.get('first_name'), 'Лилу')
        self.assertEqual(session.get('email'), 'devnull@yandex.ru')
        self.assertEqual(session.get('action'), 'signup')
        self.assertEqual(session.get('next'), '/next/')

    # def test_signup_confirmation_gravatar(self):
    #
    #     # Check request normal data
    #     request = self.factory.post(reverse('accounts-signup') + "?next=/next/", data={
    #         'username': 'test_user',
    #         'first_name': 'Лилу',
    #         'last_name': 'Казерогова',
    #         'email': 'kostya@yandex.ru',
    #         'password1': self.pwd,
    #         'password2': self.pwd,
    #     })
    #
    #     response = views.Signup.as_view()(request)
    #     self.assertEqual(response.status_code, 302)
    #
    #     self.assertEqual(len(mail.outbox), 1)
    #     body = mail.outbox[0].body
    #     gp = re.search('confirmation/email/([a-z0-9]+)/', body)
    #     self.assertRegex(gp.group(1), '^[a-z0-9]+$')
    #
    #     session_store = import_module(settings.SESSION_ENGINE).SessionStore
    #     session = session_store(session_key=gp.group(1))
    #     obj = converters.ConfirmationEmailSession().to_python(session=session.session_key)
    #     request = self.factory.get(reverse('accounts-confirmation-email', kwargs={'session': session.session_key}))
    #
    #     # adding session
    #     middleware = SessionMiddleware()
    #     middleware.process_request(request)
    #     request.session.save()
    #
    #     # adding messages
    #     setattr(request, '_messages', FallbackStorage(request))
    #     response = views.ConfirmationEmail.as_view()(request, session=obj)
    #
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, '/next/', fetch_redirect_response=False)
    #
    #     user = User.objects.get(email="kostya@yandex.ru")
    #     self.assertEqual(response.status_code, 302)
    #
    #     avatar = user.profile.avatar
    #     self.assertRegex(str(avatar), '^avatar/[0-9a-z_-]+')

    def test_signup_confirmation(self):

        # Check request normal data
        request = self.factory.post(reverse('accounts-signup') + "?next=/next/", data={
            'username': 'test_user',
            'first_name': 'Лилу',
            'last_name': 'Казерогова',
            'email': 'devnull@yandex.ru',
            'password1': 'Passw0rd12345',
            'password2': 'Passw0rd12345',
        })

        response = views.Signup.as_view()(request)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body
        gp = re.search('confirmation/email/([a-z0-9]+)/', body)
        self.assertRegex(gp.group(1), '^[a-z0-9]+$')

        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        session = session_store(session_key=gp.group(1))
        obj = converters.ConfirmationEmailSession().to_python(session=session.session_key)
        request = self.factory.get(reverse('accounts-confirmation-email', kwargs={'session': session.session_key}))

        # adding session
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        # adding messages
        setattr(request, '_messages', FallbackStorage(request))
        response = views.ConfirmationEmail.as_view()(request, session=obj)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/next/', fetch_redirect_response=False)


class OAuth(TestCase):
    def setUp(self):
        self.factory = RequestFactory(HTTP_HOST='localhost')
        self.pwd = hashlib.sha256(str('hello word').encode()).hexdigest()

    def test_oauth_completion_found_by_oauth_id(self):
        user = User.objects.create_user(username='username', password=self.pwd, email="devnull@yandex.ru")
        models.OAuth.objects.create(user=user, oauth_id="1234567890", provider=1)

        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        session = session_store()
        session['oauth_id'] = '1234567890'
        session['username'] = None
        session['email'] = 'devnull@yandex.ru'
        session['first_name'] = 'Lilu'
        session['last_name'] = 'Kazerogova'
        session['avatar'] = None
        session['provider'] = 1
        session.create()

        request = self.factory.get(reverse(
            'accounts-oauth-completion',
            kwargs={'session': session.session_key}),
        )
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        obj = converters.OAuthSession().to_python(session=session.session_key)
        response = views.OAuthCompletion.as_view()(request, session=obj)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_oauth_completion_dublicate_email(self):
        User.objects.create_user(username='username', password=self.pwd, email="devnull@yandex.ru")

        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        session = session_store()
        session['oauth_id'] = '1234567890'
        session['username'] = None
        session['email'] = 'devnull@yandex.ru'
        session['first_name'] = 'Lilu'
        session['last_name'] = 'Kazerogova'
        session['avatar'] = None
        session['provider'] = 1
        session.create()

        request = self.factory.get(reverse(
            'accounts-oauth-completion',
            kwargs={'session': session.session_key}),
        )
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        obj = converters.OAuthSession().to_python(session=session.session_key)
        response = views.OAuthCompletion.as_view()(request, session=obj)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_oauth_completion(self):
        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        session = session_store()
        session['oauth_id'] = '1234567890'
        session['username'] = None
        session['email'] = None
        session['first_name'] = 'Lilu'
        session['last_name'] = 'Kazerogova'
        session['avatar'] = None
        session['provider'] = 1
        session.create()

        request = self.factory.get(reverse('accounts-oauth-completion', kwargs={'session': session.session_key}))
        obj = converters.OAuthSession().to_python(session=session.session_key)

        response = views.OAuthCompletion.as_view()(request, session=obj)
        self.assertEqual(response.status_code, 200)
        response.render()

        # Registration completion
        request = self.factory.post(reverse(
            'accounts-oauth-completion',
            kwargs={'session': session.session_key}),
            data={'username': 'kazerogova'}
        )

        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        obj = converters.OAuthSession().to_python(session=session.session_key)
        response = views.OAuthCompletion.as_view()(request, session=obj)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/', fetch_redirect_response=False)
