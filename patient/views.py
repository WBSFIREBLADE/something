import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import PatientForm
from .models import Patient


@login_required
@require_http_methods(['GET'])
def patient_list_create(request):

    if not request.user.is_staff:
        return JsonResponse(
            {'error': 'Permission denied'},
            status=403
        )

    patients = Patient.objects.select_related('user').all()

    return render(
        request,
        'patient/patient_list.html',
        {
            'patients': patients,
            'has_patient_profile': Patient.objects.filter(
                user=request.user
            ).exists(),
        },
    )


@login_required
@require_http_methods(['GET', 'POST'])
def patient_create(request):
    profile_exists = Patient.objects.filter(user=request.user).exists()
    form = PatientForm(request.POST or None)

    if request.method == 'POST' and not profile_exists and form.is_valid():
        patient = form.save(commit=False)
        patient.user = request.user
        patient.save()
        if request.user.is_staff:
            return redirect('patient_list_create')
        return redirect('home')

    return render(
        request,
        'patient/patient_form.html',
        {'form': form, 'profile_exists': profile_exists},
    )


@login_required
@require_http_methods(['GET', 'PUT', 'PATCH', 'DELETE'])
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if not request.user.is_staff and patient.user_id != request.user.id:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    if request.method == 'GET':
        return JsonResponse({
            'id': patient.id,
            'username': patient.user.username,
            'date_of_birth': patient.date_of_birth,
            'gender': patient.gender,
            'blood_group': patient.blood_group,
            'phone_number': patient.phone_number,
            'address': patient.address,
            'zip_code': patient.zip_code,
            'emergency_contact': patient.emergency_contact,
        })

    if request.method in ['PUT', 'PATCH']:
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        allowed_fields = [
            'date_of_birth',
            'gender',
            'blood_group',
            'phone_number',
            'address',
            'zip_code',
            'emergency_contact',
        ]
        if request.method == 'PUT':
            missing_fields = [field for field in allowed_fields if field not in body]
            if missing_fields:
                return JsonResponse(
                    {'error': 'Missing required fields', 'fields': missing_fields},
                    status=400,
                )

        for field in allowed_fields:
            if field in body:
                setattr(patient, field, body[field])
        patient.save()
        return JsonResponse({'message': 'Patient updated successfully'})

    patient.delete()
    return JsonResponse({'message': 'Patient deleted successfully'})
