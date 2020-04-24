from django.urls import path, register_converter

from . import views, converters

register_converter(converters.OAuthSession, 'oauth')
register_converter(converters.ConfirmationEmailSession, 'confirmation-email')

app_name = 'django-simple-account'

urlpatterns = [
    path('login/', views.Login.as_view(), name="login"),
    path('signup/', views.Signup.as_view(), name="signup"),
    path('oauth/google/', views.OAuthGoogle.as_view(), name='oauth-google'),
    path('oauth/facebook/', views.OAuthFacebook.as_view(), name='oauth-facebook'),
    path('oauth/completion/<oauth:session>/', views.OAuthCompletion.as_view(), name='oauth-completion'),
    path(
        'confirmation/email/<confirmation-email:session>/',
        views.ConfirmationEmail.as_view(),
        name='confirmation-email'
    ),
    path('forgotpassword/', views.ForgotPassword.as_view(), name='forgotpassword'),
    path('facebook/deactivate/', views.FacebookDeactivate.as_view(), name='facebook-deactivate'),
]

# if 'rest_framework' in settings.INSTALLED_APPS:
#     urlpatterns += [
#         # path('api-auth/', include('rest_framework.urls'))
#         path('api/v1/', api.APIUser.as_view(), name='accounts-api-user'),
#         path('api/v1/<int:id>/', api.APIUserDetail.as_view(), name='accounts-api-user-detail'),
#     ]
