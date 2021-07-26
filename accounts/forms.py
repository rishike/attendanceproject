from django.forms import ModelForm
from .models import Accounts
from django.core.exceptions import ValidationError


class LoginForm(ModelForm):
    class Meta:
        model = Accounts
        fields = ['email', 'password']


class AddUserForm(ModelForm):
    class Meta:
        model = Accounts
        fields = ['username', 'name', 'email', 'password', 'type']

    def clean(self):
        super(AddUserForm, self).clean()
        password = self.cleaned_data.get('password', '')
        username = self.cleaned_data.get('username', '')
        if username:
            self.cleaned_data['username'] = username.replace(" ", "_")

        if len(password) < 6:
            self.errors['password'] = self.error_class([
                'Minimum 6 characters required for password'
            ])

        return self.cleaned_data

    # def clean_password(self):
    #     password = self.cleaned_data['password']
    #     if len(password) < 8:
    #         raise ValidationError("Password Must be 8 character long")
    #     return password
