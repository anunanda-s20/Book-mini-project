from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Book, Address, UserProfile

# ==============================
# 1️⃣ USER SIGNUP FORM
# ==============================
class SimpleUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Enter a valid email, e.g., user@gmail.com"
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap styling
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        allowed_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
        domain = email.split('@')[-1]
        if domain not in allowed_domains:
            raise forms.ValidationError(
                "Please use a valid email address from Gmail, Yahoo, Outlook, or Hotmail."
            )
        return email

# ==============================
# 2️⃣ BOOK FORM (STAFF ONLY)
# ==============================
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'price', 'description', 'stock', 'is_active', 'published_date'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter book title'}),
            'author': forms.TextInput(attrs={'placeholder': 'Enter author name'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Enter price in INR', 'min': '0', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter book description', 'rows': 4}),
            'stock': forms.NumberInput(attrs={'placeholder': 'Available quantity', 'min': '0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'published_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap 'form-control' to all fields except checkbox
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'

# ==============================
# 3️⃣ ADDRESS FORM
# ==============================
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'street', 'city', 'state', 'pincode']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True
            field.widget.attrs['class'] = 'form-control'

    # Phone validation
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit() or len(phone) not in [10, 11, 12]:
            raise forms.ValidationError("Enter a valid phone number")
        return phone

    # Pincode validation
    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if not pincode.isdigit() or len(pincode) != 6:
            raise forms.ValidationError("Enter a valid 6-digit pincode")
        return pincode

# ==============================
# 4️⃣ PROFILE EDIT FORM
# ==============================
class EditProfileForm(forms.ModelForm):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Username"
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label="Email"
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Phone",
        help_text="Optional, digits only"
    )

    class Meta:
        model = UserProfile
        fields = ['phone']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and (not phone.isdigit() or len(phone) not in [10, 11, 12]):
            raise forms.ValidationError("Enter a valid phone number")
        return phone
