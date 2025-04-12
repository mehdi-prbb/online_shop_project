import secrets
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages
from django.views.generic import CreateView
from django.contrib.auth import authenticate, login, logout

from .forms import SendOtpCodeForm, VerifyOtpCodeForm
from .models import CustomUser, OtpCode

class SendOtpCodeView(CreateView):
    model = OtpCode
    form_class = SendOtpCodeForm
    template_name = 'accounts/registration.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:

            # TODO

            messages.warning(request, 'You are already login.')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        otp_code = secrets.randbelow(900000) + 100000

        if form.is_valid():
            phone = form.cleaned_data['phone']

            try:
                otp = OtpCode.objects.create(phone=phone, code=otp_code)
                # TODO
                # send otp function instead of print
                print(otp)
                request.session['user_phone'] = {
                    'phone_number': phone
                }
                messages.success(request, 'OTP code has been sent to your phone.')
                return redirect('accounts:verify')
            # TODO
            # replace with sms service problems
            except Exception:
                messages.error(request, 'A problem occurred while processing your request. Please try again.')
        return render(request, self.template_name, {'form':form})
        

class VerifyOTPCodeView(CreateView):
    model = OtpCode
    form_class = VerifyOtpCodeForm
    template_name = 'accounts/verify.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:

            # TODO

            messages.warning(request, 'You are already login.')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        phone = request.session['user_phone']['phone_number']

        if form.is_valid():
            input_code = form.cleaned_data['code']

            try:
                otp_instance = OtpCode.objects.get(phone=phone)
            except OtpCode.DoesNotExist:
                messages.error(request, 'invalid code')
                return redirect('accounts:verify')
            
            if input_code == otp_instance.code:
                user, created = CustomUser.objects.get_or_create(phone=phone)
                if created:
                    login(request, user, backend='accounts.authenticate.MobileBackend')
                    otp_instance.delete()
                    messages.success(request, 'you register successfully')
                    return redirect('products:home')
                else:
                    login(request, user, backend='accounts.authenticate.MobileBackend')
                    otp_instance.delete()
                    messages.success(request, 'you login successfully')
                    return redirect('products:home')

            else:
                messages.error(request, 'Invalide code')
                return redirect('accounts:verify')
                
        return redirect('products:home')
