import json

from django.contrib import admin
from django.contrib.sessions.models import Session

from . import models


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'birth_date', 'phone')

    def has_add_permission(self, request):
        return False

    # def has_delete_permission(self, request, obj=None):
    #     return False


class OAuthAdmin(admin.ModelAdmin):
    list_display = ('user', 'oauth_id', 'provider')


class SessionAdmin(admin.ModelAdmin):
    @staticmethod
    def _session_data(obj):
        json_string = json.dumps(obj.get_decoded())
        return json_string

    _session_data.allow_tags = True
    list_display = ['session_key', '_session_data', 'expire_date']
    readonly_fields = ['_session_data']
    exclude = ['session_data']
    date_hierarchy = 'expire_date'


admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.OAuth, OAuthAdmin)
admin.site.register(Session, SessionAdmin)
