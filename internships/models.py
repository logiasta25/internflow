from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)

    def __str__(self):
        return self.name

class Internship(models.Model):
    MODE_CHOICES = [
        ('Remote', 'Remote'),
        ('Onsite', 'Onsite'),
        ('Hybrid', 'Hybrid'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='internships', blank=True, null=True)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    skills_required = models.TextField(blank=True, null=True)
    stipend = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=255, blank=True)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, blank=True)
    openings = models.PositiveIntegerField(blank=True, null=True)
    last_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    apply_link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        company_name = self.company.name if self.company else "Unknown Company"
        title = self.title or "Untitled Internship"
        return f"{title} at {company_name}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    phone = models.CharField(max_length=15, blank=True)
    college = models.CharField(max_length=255, blank=True)
    degree = models.CharField(max_length=255, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2)
    skills = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Application(models.Model):
    STATUS_CHOICES = [
        ('Applied', 'Applied'),
        ('Under Review', 'Under Review'),
        ('Shortlisted', 'Shortlisted'),
        ('Selected', 'Selected'),
        ('Rejected', 'Rejected'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='applications')
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Applied')
    admin_remarks = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'internship')

    def __str__(self):
        return f"{self.student.user.username} - {self.internship.title}"
