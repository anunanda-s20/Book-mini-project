from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Book, Address

# =============================
# USER SIGNUP FORM
# =============================
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
        # Add Bootstrap styling + remove default help text
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''

    # -----------------------------
    # Validate email: duplicates + allowed domains
    # -----------------------------
    def clean_email(self):
        email = self.cleaned_data.get('email')

        # ✅ Block duplicate email
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")

        # ✅ Only allow specific email domains
        allowed_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
        try:
            domain = email.split('@')[1]
        except IndexError:
            raise forms.ValidationError("Enter a valid email address.")
        
        if domain not in allowed_domains:
            raise forms.ValidationError(
                "Please use a valid email address from Gmail, Yahoo, Outlook, or Hotmail."
            )

        return email


# =============================
# BOOK FORM (STAFF ONLY)
# =============================
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title',
            'author',
            'price',
            'description',
            'stock',
            'is_active',
            'published_date'
        ]
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date'})
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
