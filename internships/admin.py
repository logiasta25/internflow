from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import Company, Internship, Student, Application

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'website')
    search_fields = ('name', 'location')

@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'mode', 'location', 'stipend', 'openings', 'last_date', 'is_active')
    list_filter = ('mode', 'is_active', 'company')
    search_fields = ('title', 'company__name', 'location')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'college', 'degree', 'cgpa', 'phone')
    search_fields = ('user__username', 'college', 'degree')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'internship', 'status', 'applied_at')
    list_filter = ('status', 'internship', 'internship__company')
    search_fields = ('student__user__username', 'internship__title')
    actions = ['mark_as_shortlisted']

    @admin.action(description='Mark selected applications as Shortlisted')
    def mark_as_shortlisted(self, request, queryset):
        # queryset.update() is removed as it doesn't fire signals and causes double writes when followed by .save()
        for application in queryset:
            application.status = 'Shortlisted'
            application.save()
        self.message_user(request, f"{queryset.count()} applications marked as Shortlisted.")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

