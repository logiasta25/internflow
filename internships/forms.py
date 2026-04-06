from django import forms
from django.contrib.auth.models import User
from .models import Student, Internship, Application, Company

class StudentRegistrationForm(forms.ModelForm):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect, initial='student')
    
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    phone = forms.CharField(max_length=15, required=False)
    college = forms.CharField(max_length=255, required=False)
    degree = forms.CharField(max_length=255, required=False)
    cgpa = forms.DecimalField(max_digits=4, decimal_places=2, required=False)
    skills = forms.CharField(widget=forms.Textarea, required=False)
    resume = forms.FileField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        role = cleaned_data.get("role")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        if role == 'student':
            required_student_fields = ['phone', 'college', 'degree', 'cgpa']
            for field in required_student_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, "This field is required for students.")
                    
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        role = self.cleaned_data.get("role")
        
        if role == 'admin':
            user.is_staff = True
            user.is_superuser = True
            
        if commit:
            user.save()
            if role == 'student':
                Student.objects.create(
                    user=user,
                    phone=self.cleaned_data.get('phone', ''),
                    college=self.cleaned_data.get('college', ''),
                    degree=self.cleaned_data.get('degree', ''),
                    cgpa=self.cleaned_data.get('cgpa', 0.0),
                    skills=self.cleaned_data.get('skills', ''),
                    resume=self.cleaned_data.get('resume')
                )
        return user

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['phone', 'college', 'degree', 'cgpa', 'skills', 'resume']

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter']

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'description', 'website', 'location', 'logo']

class InternshipForm(forms.ModelForm):
    class Meta:
        model = Internship
        fields = ['company', 'title', 'description', 'requirements', 'skills_required', 'location', 'mode', 'stipend', 'openings', 'duration', 'last_date', 'apply_link', 'is_active']
        widgets = {
            'last_date': forms.DateInput(attrs={'type': 'date'}),
        }
