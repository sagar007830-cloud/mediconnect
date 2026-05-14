from django.db import models

# Create your models here.
# core/models.py

from django.db import models
from django.contrib.auth.models import User


# ══════════════════════════════════
#  DOCTOR MODEL
# ══════════════════════════════════
class Doctor(models.Model):

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy',      'Busy'),
        ('offline',   'Off Today'),
    ]

    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor')
    specialty  = models.CharField(max_length=100)
    fee        = models.IntegerField(default=0)
    experience = models.IntegerField(default=0)
    license_no = models.CharField(max_length=100)
    rating     = models.FloatField(default=0.0)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    clinic     = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} — {self.specialty}"


# ══════════════════════════════════
#  PATIENT MODEL
# ══════════════════════════════════
class Patient(models.Model):

    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')
    phone       = models.CharField(max_length=15)
    blood_group = models.CharField(max_length=5, blank=True)
    age         = models.IntegerField(default=0)

    def __str__(self):
        return self.user.get_full_name()


# ══════════════════════════════════
#  APPOINTMENT MODEL
# ══════════════════════════════════
class Appointment(models.Model):

    STATUS_CHOICES = [
        ('booked',    'Booked'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    patient   = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor    = models.ForeignKey(Doctor,  on_delete=models.CASCADE, related_name='appointments')
    date      = models.DateField()
    time_slot = models.CharField(max_length=20)
    status    = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')
    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} → Dr. {self.doctor.user.get_full_name()} on {self.date}"


# ══════════════════════════════════
#  REVIEW MODEL
# ══════════════════════════════════
class Review(models.Model):

    patient    = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='reviews')
    doctor     = models.ForeignKey(Doctor,  on_delete=models.CASCADE, related_name='reviews')
    stars      = models.IntegerField(default=5)
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stars}⭐ for Dr. {self.doctor.user.get_full_name()} by {self.patient}"