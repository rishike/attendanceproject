from django.forms import ModelForm
from django import forms
from .models import Accounts, Captured
from django.core.exceptions import ValidationError

TYPE_CHOICES =(
    ("Admin", "Admin"),
    ("Standard User", "Standard User")
)

class CapturedForm(ModelForm):

    class Meta:
        model = Captured
        fields = ['captured']


class LoginForm(ModelForm):
    class Meta:
        model = Accounts
        fields = ['email', 'password']


class UpdateUserForm(forms.Form):
    username = forms.CharField(required=False)
    name = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    type = forms.ChoiceField(choices=TYPE_CHOICES, required=False)

    class Meta:
        model = Accounts
        fields = ['username', 'name', 'password', 'type']

    def clean(self):
        super(UpdateUserForm, self).clean()
        password = self.cleaned_data.get('password', '')
        username = self.cleaned_data.get('username', '')
        if username:
            self.cleaned_data['username'] = username.replace(" ", "_")

        if len(password) < 6:
            self.errors['password'] = self.error_class([
                'Minimum 6 characters required for password'
            ])

        return self.cleaned_data


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
