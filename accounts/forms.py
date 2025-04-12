from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.forms import ModelForm
from django import forms

from . models import CustomUser, OtpCode


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['phone']


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['phone']


class SendOtpCodeForm(forms.ModelForm):
    class Meta:
        model = OtpCode
        fields = ['phone']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if phone.isdigit() == False or not phone.startswith('09') or len(phone) != 11:
            raise forms.ValidationError('Invalid phone number')

        return phone


class VerifyOtpCodeForm(forms.ModelForm):
    class Meta:
        model = OtpCode
        fields = ['code']