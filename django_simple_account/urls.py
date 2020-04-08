from django.urls import path, register_converter

from . import views, converters

register_converter(converters.OAuthSession, 'oauth')
register_converter(converters.ConfirmationEmailSession, 'confirmation-email')

urlpatterns = [
    path('login/', views.Login.as_view(), name="accounts-login"),
    path('signup/', views.Signup.as_view(), name="accounts-signup"),
    path('oauth/google/', views.OAuthGoogle.as_view(), name='accounts-oauth-google'),
    path('oauth/facebook/', views.OAuthFacebook.as_view(), name='accounts-oauth-facebook'),
    path('oauth/completion/<oauth:session>/', views.OAuthCompletion.as_view(), name='accounts-oauth-completion'),
    path(
        'confirmation/email/<confirmation-email:session>/',
        views.ConfirmationEmail.as_view(),
        name='accounts-confirmation-email'
    ),
    path('facebook/deactivate/', views.FacebookDeactivate.as_view(), name='accounts-facebook-deactivate'),
]

# if 'rest_framework' in settings.INSTALLED_APPS:
#     urlpatterns += [
#         # path('api-auth/', include('rest_framework.urls'))
#         path('api/v1/', api.APIUser.as_view(), name='accounts-api-user'),
#         path('api/v1/<int:id>/', api.APIUserDetail.as_view(), name='accounts-api-user-detail'),
#     ]
