from django import forms

from .models import Patient


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'date_of_birth',
            'gender',
            'blood_group',
            'phone_number',
            'address',
            'zip_code',
            'emergency_contact',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(),
            'blood_group': forms.Select(),
            'phone_number': forms.TelInput(attrs={'autocomplete': 'tel'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'zip_code': forms.TextInput(attrs={'autocomplete': 'postal-code'}),
            'emergency_contact': forms.TextInput(attrs={'autocomplete': 'off'}),
        }
