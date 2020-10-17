from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import CustomUser
class LoginForm(forms.Form):
    phone=forms.IntegerField(label = 'your phone number')
    password = forms.CharField(widget = forms.PasswordInput)

class VerifyForm(forms.Form):
    key = forms.IntegerField(label = 'Please Enter OPT here')

class RegisterForm(forms.Form):
    password = forms.CharField(widget = forms.PasswordInput)
    password2 = forms.CharField(label = 'Confirm password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('phone', )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        qs = CustomUser.objects.filter(phone=phone)
        if qs.exists():
            raise forms.ValidationError("phone is taken")
        return phone

    def clean_password2(self):
        password1 = self.clean_data.get("password1")
        password2 = self.clean_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

class TempRegisterForm(forms.Form):
    phone = forms.IntegerField()
    opt = forms.IntegerField()

class SetPasswordForm(forms.Form):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

class UserAdminCreationForm(forms.Form):
    '''A form for creating new users. Includes all the required fields, plus a repeated password.'''
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('phone', )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password don't match")
        return password2

    def save(self, commit=True):
        # save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        # user.active = false

        if commit:
            user.save()
        return user

class UserAdminChangeForm(forms.ModelForm):
    '''A form for updating users. Includes all the fields on the user, but replaces the password field with admin's password hash
    display field'''

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ('phone', 'password', 'active', 'admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here rather than on the field, because the the field does not have access to the initial value
        return self.initial("password")