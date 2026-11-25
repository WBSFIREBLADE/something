from django import forms
from django.contrib.auth import get_user_model

from .models import Patient


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'user',
            'patient_name',
            'date_of_birth',
            'gender',
            'blood_group',
            'phone_number',
            'address',
            'zip_code',
            'emergency_contact',
        ]
        widgets = {
            'patient_name': forms.TextInput(attrs={'autocomplete': 'name'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(),
            'blood_group': forms.Select(),
            'phone_number': forms.TelInput(attrs={'autocomplete': 'tel'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'zip_code': forms.TextInput(attrs={'autocomplete': 'postal-code'}),
            'emergency_contact': forms.TextInput(attrs={'autocomplete': 'off'}),
        }

    def __init__(self, *args, account_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient_name'].required = True

        if account_user and account_user.is_staff:
            user_model = get_user_model()
            self.fields['user'].queryset = (
                user_model.objects
                .filter(patient_profile__isnull=True)
                .order_by('username')
            )
            self.fields['user'].label = 'Patient account'
            self.fields['user'].empty_label = 'Choose an account'
        else:
            self.fields.pop('user')
            if account_user:
                self.initial.setdefault('patient_name', account_user.username)
