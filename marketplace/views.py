from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Q

from .models import WorkerProfile, Review, SKILL_CHOICES, LOCATION_CHOICES, AVAILABILITY_CHOICES
from .forms import WorkerRegistrationForm, WorkerProfileForm, ReviewForm

def home_view(request):
    workers = WorkerProfile.objects.all().order_by('-is_premium', '-id')

    # Get search parameters
    query = request.GET.get('q', '')
    skill_filter = request.GET.get('skill', '')
    location_filter = request.GET.get('location', '')
    availability_filter = request.GET.get('availability', '')

    if query:
        workers = workers.filter(Q(name__icontains=query) | Q(bio__icontains=query))
    if skill_filter:
        workers = workers.filter(skill=skill_filter)
    if location_filter:
        workers = workers.filter(location=location_filter)
    if availability_filter:
        workers = workers.filter(availability=availability_filter)

    # Statistics
    total_workers = WorkerProfile.objects.count()
    available_today = WorkerProfile.objects.filter(availability='available').count()
    premium_count = WorkerProfile.objects.filter(is_premium=True).count()

    context = {
        'workers': workers,
        'skills': SKILL_CHOICES,
        'locations': LOCATION_CHOICES,
        'availabilities': AVAILABILITY_CHOICES,
        'total_workers': total_workers,
        'available_today': available_today,
        'premium_count': premium_count,
        # Keep selected filters in form inputs
        'query': query,
        'selected_skill': skill_filter,
        'selected_location': location_filter,
        'selected_availability': availability_filter,
    }
    return render(request, 'marketplace/home.html', context)

def worker_detail_view(request, pk):
    worker = get_object_or_404(WorkerProfile, pk=pk)
    reviews = worker.reviews.all().order_by('-created_at')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.worker = worker
            review.save()
            messages.success(request, f"Review submitted successfully for {worker.name}!")
            return redirect('worker_detail', pk=pk)
    else:
        form = ReviewForm()

    context = {
        'worker': worker,
        'reviews': reviews,
        'form': form,
    }
    return render(request, 'marketplace/worker_detail.html', context)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = WorkerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save()
            # Log the user in
            login(request, profile.user)
            messages.success(request, "Registration successful! Welcome to Labor Connect Gujarat.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = WorkerRegistrationForm()
        
    return render(request, 'marketplace/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect('dashboard')
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'marketplace/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

@login_required
def dashboard_view(request):
    try:
        profile = request.user.worker_profile
    except WorkerProfile.DoesNotExist:
        messages.error(request, "No worker profile found. Please register as a worker.")
        return redirect('home')

    # Handle quick availability status updates via GET parameters
    new_status = request.GET.get('status')
    if new_status in ['available', 'busy', 'soon']:
        profile.availability = new_status
        profile.save()
        messages.success(request, f"Your availability status has been updated to '{profile.get_availability_display()}'.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = WorkerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Failed to update profile. Please check the errors.")
    else:
        form = WorkerProfileForm(instance=profile)

    context = {
        'profile': profile,
        'form': form,
    }
    return render(request, 'marketplace/dashboard.html', context)
