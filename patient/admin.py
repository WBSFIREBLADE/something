from django.contrib import admin
from .models import (
    Patient,
    PatientMedicalRecord,
    PatientAppointment,
    PatientPrescription
)


# Medical Records Inline
class PatientMedicalRecordInline(admin.TabularInline):
    model = PatientMedicalRecord
    extra = 1
    show_change_link = True


# Appointment Inline
class PatientAppointmentInline(admin.TabularInline):
    model = PatientAppointment
    extra = 1
    show_change_link = True


# Prescription Inline
class PatientPrescriptionInline(admin.TabularInline):
    model = PatientPrescription
    extra = 1
    show_change_link = True


# Main Patient Admin
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'gender',
        'blood_group',
        'phone_number',
        'created_at'
    )

    search_fields = (
        'user__username',
        'user__email',
        'phone_number'
    )

    list_filter = (
        'gender',
        'blood_group',
        'created_at'
    )

    readonly_fields = (
        'created_at',
        'updated_at'
    )

    inlines = [
        PatientMedicalRecordInline,
        PatientAppointmentInline,
        PatientPrescriptionInline
    ]