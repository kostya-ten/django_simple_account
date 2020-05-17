import datetime
import os

from django.conf import settings as data_settings
from django.core.handlers.wsgi import WSGIRequest


def year(request: WSGIRequest):
    return {'YEAR': datetime.datetime.now().year}


def settings(request: WSGIRequest):
    oauth_google_client_id = getattr(data_settings, 'OAUTH_GOOGLE_CLIENT_ID', os.environ.get('OAUTH_GOOGLE_CLIENT_ID'))
    oauth_facebook_client_id = getattr(data_settings, 'OAUTH_FACEBOOK_CLIENT_ID', os.environ.get('OAUTH_FACEBOOK_CLIENT_ID'))
    return {
        'SETTINGS': data_settings,
        'DEBUG': data_settings.DEBUG,
        'OAUTH_GOOGLE_CLIENT_ID': oauth_google_client_id,
        'OAUTH_FACEBOOK_CLIENT_ID': oauth_facebook_client_id,
    }
