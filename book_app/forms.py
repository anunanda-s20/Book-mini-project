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


from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book #taking the structure of Book-model
        fields = ['title', 'author', 'price', 'published_date']#apply required fields
