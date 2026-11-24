import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from .models import Patient


@login_required
@require_http_methods(["GET", "POST"])
def patient_list_create(request):

    # GET: List all patients (admin only)
    if request.method == "GET":

        if not request.user.is_staff:
            return JsonResponse(
                {"error": "Permission denied"},
                status=403
            )

        patients = Patient.objects.select_related("user").all()

        return render(
            request,
            "patient/patient_list.html",
            {"patients": patients},
        )

    # POST: Create patient
    if request.method == "POST":

        if Patient.objects.filter(user=request.user).exists():
            return JsonResponse(
                {"error": "Patient profile already exists"},
                status=400
            )

        try:
            body = json.loads(request.body)

            patient = Patient.objects.create(
                user=request.user,
                date_of_birth=body.get("date_of_birth"),
                gender=body.get("gender"),
                blood_group=body.get("blood_group"),
                phone_number=body.get("phone_number", ""),
                address=body.get("address", ""),
                zip_code=body.get("zip_code", ""),
                emergency_contact=body.get("emergency_contact", "")
            )

            return JsonResponse({
                "message": "Patient created successfully",
                "patient_id": patient.id
            }, status=201)

        except (json.JSONDecodeError, TypeError):
            return JsonResponse(
                {"error": "Invalid JSON"},
                status=400
            )


@login_required
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def patient_detail(request, pk):

    patient = get_object_or_404(Patient, pk=pk)

    # Authorization
    if not request.user.is_staff and patient.user_id != request.user.id:
        return JsonResponse(
            {"error": "Permission denied"},
            status=403
        )

    # GET
    if request.method == "GET":

        data = {
            "id": patient.id,
            "username": patient.user.username,
            "date_of_birth": patient.date_of_birth,
            "gender": patient.gender,
            "blood_group": patient.blood_group,
            "phone_number": patient.phone_number,
            "address": patient.address,
            "zip_code": patient.zip_code
        }

        return JsonResponse(data)

    # PUT / PATCH
    if request.method in ["PUT", "PATCH"]:

        try:
            body = json.loads(request.body)

        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON"},
                status=400
            )

        allowed_fields = [
            "date_of_birth",
            "gender",
            "blood_group",
            "phone_number",
            "address",
            "zip_code",
            "emergency_contact"
        ]

        if request.method == "PUT":
            missing_fields = [
                field for field in allowed_fields
                if field not in body
            ]

            if missing_fields:
                return JsonResponse(
                    {"error": "Missing required fields", "fields": missing_fields},
                    status=400
                )

        for field in allowed_fields:
            if field in body:
                setattr(patient, field, body[field])

        patient.save()

        return JsonResponse({
            "message": "Patient updated successfully"
        })

    # DELETE
    if request.method == "DELETE":

        patient.delete()

        return JsonResponse(
            {"message": "Patient deleted successfully"},
            status=200
        )
