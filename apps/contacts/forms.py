from django import forms
from .models import Contact


class ContactForm(forms.ModelForm):
    privacy_agreed = forms.BooleanField(
        required=True,
        error_messages={'required': "Maxfiylik siyosatiga rozilik bildirishingiz shart."}
    )

    def __init__(self, *args, **kwargs):
        if args and len(args) > 0 and hasattr(args[0], 'copy'):
            data = args[0].copy()
            if 'privacy' in data and 'privacy_agreed' not in data:
                data['privacy_agreed'] = data['privacy']
            if data.get('contact_type') == 'inquiry':
                data['contact_type'] = 'general'
            args = (data,) + args[1:]
        elif 'data' in kwargs and hasattr(kwargs['data'], 'copy'):
            data = kwargs['data'].copy()
            if 'privacy' in data and 'privacy_agreed' not in data:
                data['privacy_agreed'] = data['privacy']
            if data.get('contact_type') == 'inquiry':
                data['contact_type'] = 'general'
            kwargs['data'] = data
        super().__init__(*args, **kwargs)

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
