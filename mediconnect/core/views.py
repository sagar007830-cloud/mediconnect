from django.shortcuts import render

# Create your views here.
# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Doctor, Patient, Appointment, Review


# ══════════════════════════════════
#  HOME PAGE
# ══════════════════════════════════
def home(request):
    # Sirf available doctors dikhao home pe
    doctors = Doctor.objects.filter(status='available')
    return render(request, 'index.html', {'doctors': doctors})


# ══════════════════════════════════
#  ALL DOCTORS LIST + SEARCH
# ══════════════════════════════════
def doctor_list(request):
    query = request.GET.get('q', '')  # search query

    if query:
        # Search by name ya specialty
        doctors = Doctor.objects.filter(
            specialty__icontains=query
        ) | Doctor.objects.filter(
            user__first_name__icontains=query
        )
    else:
        doctors = Doctor.objects.all()

    return render(request, 'doctors.html', {
        'doctors': doctors,
        'query': query
    })


# ══════════════════════════════════
#  DOCTOR DETAIL PAGE
# ══════════════════════════════════
def doctor_detail(request, doctor_id):
    doctor  = get_object_or_404(Doctor, id=doctor_id)
    reviews = Review.objects.filter(doctor=doctor).order_by('-created_at')
    return render(request, 'doctor_detail.html', {
        'doctor': doctor,
        'reviews': reviews
    })


# ══════════════════════════════════
#  PATIENT SIGNUP
# ══════════════════════════════════
def signup_view(request):
    if request.method == 'POST':
        role       = request.POST.get('role')        # 'patient' ya 'doctor'
        full_name  = request.POST.get('full_name')
        email      = request.POST.get('email')
        phone      = request.POST.get('phone')
        password1  = request.POST.get('password1')
        password2  = request.POST.get('password2')

        # ── Validation ──
        if password1 != password2:
            messages.error(request, 'Passwords do not match!')
            return redirect('signup')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('signup')

        # ── Create User ──
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name  = name_parts[1] if len(name_parts) > 1 else ''

        user = User.objects.create_user(
            username   = email,
            email      = email,
            password   = password1,
            first_name = first_name,
            last_name  = last_name
        )

        # ── Create Patient Profile ──
        if role == 'patient':
            Patient.objects.create(
                user        = user,
                phone       = phone,
                blood_group = request.POST.get('blood_group', ''),
                age         = request.POST.get('age', 0)
            )
            messages.success(request, '🎉 Account created! Please verify OTP.')
            request.session['verify_phone'] = phone  # phone session me save karo
            return redirect('otp_verify')

        # ── Create Doctor Profile ──
        elif role == 'doctor':
            Doctor.objects.create(
                user       = user,
                specialty  = request.POST.get('specialty', ''),
                fee        = request.POST.get('fee', 0),
                experience = request.POST.get('experience', 0),
                license_no = request.POST.get('license_no', ''),
                status     = 'available'
            )
            messages.success(request, '🎉 Doctor account created! Please verify OTP.')
            request.session['verify_phone'] = phone
            return redirect('otp_verify')
 
    return render(request, 'signup.html')


# ══════════════════════════════════
#  LOGIN
# ══════════════════════════════════
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email    = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'✅ Welcome back, {user.first_name}!')

            # Doctor hai toh dashboard pe bhejo
            if hasattr(user, 'doctor'):
                return redirect('doctor_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, '❌ Invalid email or password!')

    return render(request, 'login.html')


# ══════════════════════════════════
#  LOGOUT
# ══════════════════════════════════
def logout_view(request):
    logout(request)
    messages.success(request, '👋 Logged out successfully!')
    return redirect('home')


# ══════════════════════════════════
#  BOOK APPOINTMENT
# ══════════════════════════════════
@login_required(login_url='login')
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == 'POST':
        date      = request.POST.get('date')
        time_slot = request.POST.get('slot')

        # Patient object lao
        try:
            patient = request.user.patient
        except:
            messages.error(request, '❌ Only patients can book appointments!')
            return redirect('home')

        # Already booked check
        already_booked = Appointment.objects.filter(
            doctor    = doctor,
            date      = date,
            time_slot = time_slot
        ).exists()

        if already_booked:
            messages.error(request, '❌ This slot is already booked!')
            return redirect('book', doctor_id=doctor_id)

        # Booking save karo
        Appointment.objects.create(
            patient   = patient,
            doctor    = doctor,
            date      = date,
            time_slot = time_slot,
            status    = 'booked'
        )

        messages.success(request, f'✅ Appointment booked with Dr. {doctor.user.get_full_name()}!')
        return redirect('appointments')

    return render(request, 'book.html', {'doctor': doctor})


# ══════════════════════════════════
#  MY APPOINTMENTS (Patient)
# ══════════════════════════════════
@login_required(login_url='login')
def appointments(request):
    try:
        patient      = request.user.patient
        appointments = Appointment.objects.filter(
            patient=patient
        ).order_by('-date')
    except:
        appointments = []

    return render(request, 'appointments.html', {
        'appointments': appointments
    })


# ══════════════════════════════════
#  SUBMIT REVIEW / RATING
# ══════════════════════════════════
@login_required(login_url='login')
def submit_review(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == 'POST':
        stars   = int(request.POST.get('stars', 5))
        comment = request.POST.get('comment', '')

        try:
            patient = request.user.patient
        except:
            messages.error(request, '❌ Only patients can submit reviews!')
            return redirect('home')

        # Review save karo
        Review.objects.create(
            patient = patient,
            doctor  = doctor,
            stars   = stars,
            comment = comment
        )

        # Doctor ka average rating update karo
        all_reviews   = Review.objects.filter(doctor=doctor)
        total_stars   = sum(r.stars for r in all_reviews)
        doctor.rating = round(total_stars / all_reviews.count(), 1)
        doctor.save()

        messages.success(request, '⭐ Review submitted successfully!')
        return redirect('doctor_detail', doctor_id=doctor_id)

    return redirect('doctor_detail', doctor_id=doctor_id)


# ══════════════════════════════════
#  MEDICAL TESTS PAGE
# ══════════════════════════════════
def tests(request):
    return render(request, 'tests.html')


# ══════════════════════════════════
#  PATIENT PROFILE
# ══════════════════════════════════
@login_required(login_url='login')
def profile(request):
    try:
        patient = request.user.patient
    except:
        patient = None

    return render(request, 'profile.html', {'patient': patient})


# ══════════════════════════════════
#  DOCTOR DASHBOARD
# ══════════════════════════════════
@login_required(login_url='login')
def doctor_dashboard(request):
    try:
        doctor = request.user.doctor
    except:
        messages.error(request, '❌ Doctor account not found!')
        return redirect('home')

    # Aaj ke appointments
    from datetime import date
    todays_appointments = Appointment.objects.filter(
        doctor = doctor,
        date   = date.today()
    ).order_by('time_slot')

    return render(request, 'doctor_dashboard.html', {
        'doctor': doctor,
        'appointments': todays_appointments
    })


# ══════════════════════════════════
#  DOCTOR STATUS UPDATE
# ══════════════════════════════════
@login_required(login_url='login')
def update_status(request):
    if request.method == 'POST':
        try:
            doctor        = request.user.doctor
            doctor.status = request.POST.get('status', 'available')
            doctor.save()
            messages.success(request, f'✅ Status updated to {doctor.status}!')
        except:
            messages.error(request, '❌ Error updating status!')

    return redirect('doctor_dashboard')
# ══════════════════════════════════
#  OTP VERIFICATION
# ══════════════════════════════════
# ══════════════════════════════════
#  OTP VERIFICATION
# ══════════════════════════════════
def otp_verify(request):
    phone = request.session.get('verify_phone', '')
    return render(request, 'otp_verification.html', {
        'phone': phone
    })
