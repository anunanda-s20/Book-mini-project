from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Book, Address  # Address for checkout/profile

# =============================
# USER SIGNUP FORM
# =============================
class SimpleUserCreationForm(UserCreationForm):
    username = forms.CharField(max_length=150, help_text='')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, help_text='')
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput, help_text='')
    email = forms.EmailField(required=True)  # ✅ Required email

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap styling to all fields
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''  # clean UI

# =============================
# BOOK FORM (STAFF)
# =============================
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'price', 'description', 'stock', 'is_active', 'published_date']
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date'})  # date picker
        }

# =============================
# ADDRESS FORM (CHECKOUT / PROFILE)
# =============================
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'street', 'city', 'state', 'pincode']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Make all fields required + Bootstrap styling
        for field in self.fields.values():
            field.required = True
            field.widget.attrs['class'] = 'form-control'

    # -----------------------------
    # Validate phone number
    # -----------------------------
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit() or len(phone) not in [10, 11, 12]:
            raise forms.ValidationError("Enter a valid phone number")
        return phone

    # -----------------------------
    # Validate pincode
    # -----------------------------
    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if not pincode.isdigit() or len(pincode) != 6:
            raise forms.ValidationError("Enter a valid 6-digit pincode")
        return pincode
