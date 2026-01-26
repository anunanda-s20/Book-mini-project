from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Book, Address  # Address for checkout form

# =============================
# USER SIGNUP FORM
# =============================
class SimpleUserCreationForm(UserCreationForm):
    username = forms.CharField(max_length=150, help_text='')  # username input
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, help_text='')  # password
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput, help_text='')  # confirm password

    class Meta:
        model = User
        fields = ("username", "password1", "password2")


# =============================
# BOOK FORM (DASHBOARD)
# =============================
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title',           # book name
            'author',          # author name
            'price',           # price
            'description',     # optional description
            'stock',           # available quantity
            'is_active',       # show/hide book
            'published_date'   # optional published date
        ]
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date'})  # date picker
        }


# =============================
# ADDRESS FORM (FOR CHECKOUT)
# =============================
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'street', 'city', 'state', 'pincode']  # fields user may fill

    # -----------------------------
    # Make all fields optional (mini project friendly)
    # -----------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False  # no field blocks submission

    # -----------------------------
    # Validate phone if entered
    # -----------------------------
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:  # only check if user entered
            if not phone.isdigit() or len(phone) not in [10, 11, 12]:
                raise forms.ValidationError("Enter a valid phone number")
        return phone

    # -----------------------------
    # Validate pincode if entered
    # -----------------------------
    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if pincode:  # only check if user entered
            if not pincode.isdigit() or len(pincode) != 6:
                raise forms.ValidationError("Enter a valid 6-digit pincode")
        return pincode
