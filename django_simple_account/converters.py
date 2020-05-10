from importlib import import_module

from django.conf import settings


class OAuthSession:
    """Converters url OAuth session."""

    regex = '[a-z0-9]+'

    def __init__(self):
        self.username = None
        self.last_name = None
        self.first_name = None
        self.email = None
        self.session = None
        self.oauth_id = None
        self.provider = None
        self.avatar = None

    def to_python(self, session):
        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        self.session = session_store(session_key=session)

        for item in ['username', 'first_name', 'last_name', 'email', 'oauth_id', 'provider', 'avatar']:
            setattr(self, item, self.session.get(item))

        return self

    @staticmethod
    def to_url(session):
        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        obj = session_store(session_key=session)

        if obj is None:
            raise ValueError('Session not found')

        return session


class ConfirmationEmailSession:

    """Converters url Confirmation email session"""
    regex = '[a-z0-9]+'

    def __init__(self):
        self.username = None
        self.last_name = None
        self.first_name = None
        self.email = None
        self.password1 = None
        self.password2 = None
        self.session = None
        self.action = None
        self.next = '/'

    def to_python(self, session):
        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        self.session = session_store(session_key=session)

        for item in ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'action', 'next']:
            setattr(self, item, self.session.get(item))

        return self

    @staticmethod
    def to_url(session):
        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        obj = session_store(session_key=session)

        if obj is None:
            raise ValueError('Session not found')

        return session


class ConfirmationForgotPasswordSession:

    """Converters url Confirmation email session"""
    regex = '[a-z0-9]+'

    def __init__(self):
        self.email = None
        self.action = None
        self.session = None
        self.next = '/'

    def to_python(self, session):
        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        self.session = session_store(session_key=session)

        for item in ['email', 'action']:
            setattr(self, item, self.session.get(item))

        return self

    @staticmethod
    def to_url(session):
        session_store = import_module(settings.SESSION_ENGINE).SessionStore
        obj = session_store(session_key=session)

        if obj is None:
            raise ValueError('Session not found')

        return session
