from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Company, Internship, Student, Application
from .forms import StudentRegistrationForm, StudentProfileForm, ApplicationForm, CompanyForm, InternshipForm

def home(request):
    total_companies = Company.objects.count()
    total_internships = Internship.objects.count()
    total_placed = Application.objects.filter(status='Selected').count()
    featured_internships = Internship.objects.filter(is_active=True).order_by('-created_at')[:3]
    return render(request, 'internships/home.html', {
        'total_companies': total_companies,
        'total_internships': total_internships,
        'total_placed': total_placed,
        'featured_internships': featured_internships,
    })

def register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def internship_list(request):
    query = request.GET.get('q')
    mode = request.GET.get('mode')
    location = request.GET.get('location')
    stipend_min = request.GET.get('stipend_min')
    stipend_max = request.GET.get('stipend_max')
    sort = request.GET.get('sort', 'latest')

    internships = Internship.objects.filter(is_active=True).annotate(application_count=Count('applications'))

    # Filtering
    if query:
        internships = internships.filter(Q(title__icontains=query) | Q(company__name__icontains=query))
    if mode:
        internships = internships.filter(mode=mode)
    if location:
        internships = internships.filter(location__icontains=location)
    if stipend_min:
        internships = internships.filter(stipend__gte=stipend_min)
    if stipend_max:
        internships = internships.filter(stipend__lte=stipend_max)

    # Sorting
    if sort == 'stipend_high':
        internships = internships.order_by('-stipend')
    elif sort == 'stipend_low':
        internships = internships.order_by('stipend')
    elif sort == 'deadline':
        internships = internships.order_by('last_date')
    else:
        internships = internships.order_by('-created_at')

    paginator = Paginator(internships, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'internships/list.html', {
        'internships': page_obj,
        'today': timezone.now().date(),
        'closing_soon_date': timezone.now().date() + timedelta(days=5)
    })

@login_required
def internship_detail(request, pk):
    internship = get_object_or_404(Internship, pk=pk)
    has_applied = False
    application = None
    if hasattr(request.user, 'student_profile'):
        application = Application.objects.filter(student=request.user.student_profile, internship=internship).first()
        has_applied = application is not None

    return render(request, 'internships/detail.html', {
        'internship': internship,
        'has_applied': has_applied,
        'application': application,
        'today': timezone.now().date(),
        'closing_soon_date': timezone.now().date() + timedelta(days=5)
    })

@login_required
def apply_internship(request, pk):
    if request.user.is_staff or not hasattr(request.user, 'student_profile'):
        messages.error(request, "Only students can apply for internships.")
        return redirect('internship_list')

    internship = get_object_or_404(Internship, pk=pk)
    student = request.user.student_profile

    # Check if already applied
    if Application.objects.filter(student=student, internship=internship).exists():
        messages.warning(request, "You have already applied for this internship.")
        return redirect('internship_detail', pk=pk)

    # Check openings
    applied_count = Application.objects.filter(internship=internship).exclude(status='Rejected').count()
    if applied_count >= internship.openings:
        messages.error(request, "No openings available for this internship.")
        return redirect('internship_detail', pk=pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = student
            application.internship = internship
            application.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('dashboard')
    else:
        form = ApplicationForm()
    
    return render(request, 'internships/apply.html', {'form': form, 'internship': internship})

@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    if not hasattr(request.user, 'student_profile'):
        messages.error(request, "You need a student profile to access the dashboard.")
        return redirect('home')

    status_filter = request.GET.get('status')
    applications = Application.objects.filter(student=request.user.student_profile).order_by('-applied_at')
    
    if status_filter:
        applications = applications.filter(status=status_filter)
        
    return render(request, 'internships/dashboard.html', {
        'applications': applications,
        'status_filter': status_filter
    })

@login_required
def profile(request):
    if request.user.is_staff or not hasattr(request.user, 'student_profile'):
        messages.error(request, "Only students have a profile.")
        return redirect('home')

    student = request.user.student_profile
    if request.method == 'POST':
        u_form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        u_form = StudentProfileForm(instance=student)
    
    # Calculate stats
    apps = Application.objects.filter(student=student)
    stats = {
        'total': apps.count(),
        'shortlisted': apps.filter(status='Shortlisted').count(),
        'selected': apps.filter(status='Selected').count(),
        'rejected': apps.filter(status='Rejected').count(),
    }
    
    return render(request, 'internships/profile.html', {
        'u_form': u_form,
        'stats': stats
    })

@login_required
def withdraw_application(request, pk):
    if request.user.is_staff or not hasattr(request.user, 'student_profile'):
        messages.error(request, "Only students can withdraw applications.")
        return redirect('home')

    application = get_object_or_404(Application, pk=pk, student=request.user.student_profile)
    if application.status == 'Applied':
        application.delete()
        messages.success(request, "Application withdrawn successfully.")
    else:
        messages.error(request, "You can only withdraw applications with 'Applied' status.")
    return redirect('dashboard')

@staff_member_required
def admin_dashboard(request):
    stats = {
        'total_students': Student.objects.count(),
        'total_internships': Internship.objects.count(),
        'total_applications': Application.objects.count(),
        'status_breakdown': Application.objects.values('status').annotate(count=Count('status')),
    }
    # For Chart.js
    status_data = list(Application.objects.values('status').annotate(count=Count('status')))
    return render(request, 'internships/admin_dashboard.html', {
        'stats': stats,
        'status_data_json': status_data
    })

# --- Admin Application Views ---
@staff_member_required
def admin_application_list(request):
    query = request.GET.get('q')
    status_filter = request.GET.get('status')
    
    applications = Application.objects.all().order_by('-applied_at')
    
    if query:
        applications = applications.filter(
            Q(student__user__username__icontains=query) | 
            Q(internship__title__icontains=query)
        )
    if status_filter:
        applications = applications.filter(status=status_filter)
        
    paginator = Paginator(applications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'internships/admin_application_list.html', {
        'applications': page_obj,
        'status_choices': dict(Application.STATUS_CHOICES)
    })

@staff_member_required
def admin_application_update(request, pk):
    application = get_object_or_404(Application, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        admin_remarks = request.POST.get('admin_remarks')
        if status in dict(Application.STATUS_CHOICES):
            application.status = status
            application.admin_remarks = admin_remarks
            application.save()
            messages.success(request, f"Application status updated to {status}.")
            return redirect('admin_application_list')
    return render(request, 'internships/admin_application_update.html', {'application': application})

# --- Admin Internship Views ---
@staff_member_required
def admin_internship_list(request):
    internships = Internship.objects.all().order_by('-created_at')
    
    paginator = Paginator(internships, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'internships/admin_internship_list.html', {'internships': page_obj})

@staff_member_required
def admin_internship_create(request):
    if request.method == 'POST':
        form = InternshipForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Internship created successfully.")
            return redirect('admin_internship_list')
    else:
        form = InternshipForm()
    return render(request, 'internships/admin_internship_form.html', {'form': form, 'title': 'Create Internship'})

@staff_member_required
def admin_internship_update(request, pk):
    internship = get_object_or_404(Internship, pk=pk)
    if request.method == 'POST':
        form = InternshipForm(request.POST, instance=internship)
        if form.is_valid():
            form.save()
            messages.success(request, "Internship updated successfully.")
            return redirect('admin_internship_list')
    else:
        form = InternshipForm(instance=internship)
    return render(request, 'internships/admin_internship_form.html', {'form': form, 'title': 'Edit Internship'})

@staff_member_required
def admin_internship_delete(request, pk):
    internship = get_object_or_404(Internship, pk=pk)
    if request.method == 'POST':
        internship.delete()
        messages.success(request, "Internship deleted successfully.")
        return redirect('admin_internship_list')
    return render(request, 'internships/admin_confirm_delete.html', {
        'object': internship, 
        'cancel_url': reverse('admin_internship_list')
    })

# --- Admin Company Views ---
@staff_member_required
def admin_company_list(request):
    companies = Company.objects.all().order_by('name')
    return render(request, 'internships/admin_company_list.html', {'companies': companies})

@staff_member_required
def admin_company_create(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Company created successfully.")
            return redirect('admin_company_list')
    else:
        form = CompanyForm()
    return render(request, 'internships/admin_company_form.html', {'form': form, 'title': 'Create Company'})

@staff_member_required
def admin_company_update(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, "Company updated successfully.")
            return redirect('admin_company_list')
    else:
        form = CompanyForm(instance=company)
    return render(request, 'internships/admin_company_form.html', {'form': form, 'title': 'Edit Company'})

@staff_member_required
def admin_company_delete(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        company.delete()
        messages.success(request, "Company deleted successfully.")
        return redirect('admin_company_list')
    return render(request, 'internships/admin_confirm_delete.html', {
        'object': company, 
        'cancel_url': reverse('admin_company_list')
    })

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_403(request, exception=None):
    return render(request, '403.html', status=403)
