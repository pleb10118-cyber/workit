from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomerSupport

class CustomUserCreationForm(UserCreationForm):
    is_retailer = forms.BooleanField(required=False, label='Sign up as retailer')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_retailer', 'password1', 'password2']


class CustomerSupportForm(forms.ModelForm):
    class Meta:
        model = CustomerSupport
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Enter your issue here...',
            })
        }