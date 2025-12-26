from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SimpleUserCreationForm(UserCreationForm):
    # Remove help texts
    username = forms.CharField(max_length=150, help_text='')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, help_text='')
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput, help_text='')

    class Meta:
        model = User
        fields = ("username", "password1", "password2")
