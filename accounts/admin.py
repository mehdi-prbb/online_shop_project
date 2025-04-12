from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser, OtpCode


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    form_add = CustomUserCreationForm

    list_display = ('phone', 'email', 'is_staff', 'is_superuser')
    list_filter = ('is_staff',)
    readonly_fields = ('last_login',)

    fieldsets = (
        (None, {'fields':('phone', 'email', 'password', 'username', 'first_name', 'last_name')}),
        ('permissions', {'fields':('is_active', 'is_staff', 'is_superuser', 'last_login', 'groups', 'user_permissions')})
    )

    add_fieldsets = (
        (None, {'fields':('phone', 'password1', 'password2')}),
    )

    search_fields = ('email', 'phone')
    ordering = ('phone',)
    filter_horizontal = ('groups', 'user_permissions')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            form.base_fields['is_superuser'].disabled = True
        return form
    

@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'phone', 'created_at']