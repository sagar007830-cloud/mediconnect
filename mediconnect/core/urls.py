# core/urls.py

from django.urls import path
from . import views

urlpatterns = [

    # ── HOME ──
    path('',
         views.home,
         name='home'),

    # ── DOCTORS ──
    path('doctors/',
         views.doctor_list,
         name='doctors'),

    path('doctors/<int:doctor_id>/',
         views.doctor_detail,
         name='doctor_detail'),

    # ── AUTH ──
    path('login/',
         views.login_view,
         name='login'),

    path('signup/',
         views.signup_view,
         name='signup'),

    path('logout/',
         views.logout_view,
         name='logout'),

    # ── BOOKING ──
    path('book/<int:doctor_id>/',
         views.book_appointment,
         name='book'),

    path('appointments/',
         views.appointments,
         name='appointments'),

    # ── REVIEW ──
    path('review/<int:doctor_id>/',
         views.submit_review,
         name='review'),

    # ── TESTS ──
    path('tests/',
         views.tests,
         name='tests'),

    # ── PROFILE ──
    path('profile/',
         views.profile,
         name='profile'),

    # ── DOCTOR DASHBOARD ──
    path('dashboard/',
         views.doctor_dashboard,
         name='doctor_dashboard'),

    path('update-status/',
         views.update_status,
         name='update_status'),
         
    path('otp-verify/',
         views.otp_verify,
         name='otp_verify'),  
]