from django.urls import path

from . import views


app_name = 'accounts'

urlpatterns = [
    path('registration', views.SendOtpCodeView.as_view(), name='registration'),
    path('verify-code', views.VerifyOTPCodeView.as_view(), name='verify'),
]
