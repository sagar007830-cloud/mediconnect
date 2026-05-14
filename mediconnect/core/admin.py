from django.contrib import admin
from .models import Doctor, Patient, Appointment, Review

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'specialty', 'fee', 'rating', 'status']
    list_filter  = ['status', 'specialty']
    search_fields= ['user__first_name', 'specialty']

    def get_name(self, obj):
        return f"Dr. {obj.user.get_full_name()}"
    get_name.short_description = 'Doctor Name'


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'phone', 'blood_group', 'age']

    def get_name(self, obj):
        return obj.user.get_full_name()
    get_name.short_description = 'Patient Name'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'date', 'time_slot', 'status']
    list_filter  = ['status', 'date']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'stars', 'created_at']