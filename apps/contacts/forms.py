from django import forms
from .models import Contact


class ContactForm(forms.ModelForm):
    privacy_agreed = forms.BooleanField(
        required=True,
        error_messages={'required': "Maxfiylik siyosatiga rozilik bildirishingiz shart."}
    )

    class Meta:
        model = Contact
        fields = ['full_name', 'phone', 'email', 'contact_type', 'subject', 'message', 'privacy_agreed']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ism va familiyangizni kiriting',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+998 90 123 45 67',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'nomingiz@example.com',
            }),
            'contact_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Murojaat mavzusi',
                'required': True,
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Xabaringizni bu yerga yozing...',
                'required': True,
            }),
            'privacy_agreed': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get('phone')
        email = cleaned_data.get('email')

        if not phone and not email:
            raise forms.ValidationError("Iltimos, telefon raqamingiz yoki elektron pochtangizdan kamida birini kiriting.")

        return cleaned_data
