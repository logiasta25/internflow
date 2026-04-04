from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Company, Internship, Student, Application
from .forms import StudentRegistrationForm
import datetime

class CompanyModelTest(TestCase):
    def test_company_creation_no_logo(self):
        company = Company.objects.create(
            name="Test Corp",
            description="A test company",
            website="https://test.com",
            location="Remote"
        )
        self.assertEqual(str(company), "Test Corp")
        self.assertIsNone(company.logo.name)

class InternshipModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Corp")

    def test_internship_apply_link(self):
        internship = Internship.objects.create(
            company=self.company,
            title="SDE Intern",
            description="Dev role",
            requirements="Python",
            skills_required="Django",
            stipend=5000,
            duration="3 months",
            location="Remote",
            mode="Remote",
            openings=5,
            last_date=datetime.date.today(),
            apply_link="https://external.apply.com"
        )
        self.assertEqual(internship.apply_link, "https://external.apply.com")

class StudentRegistrationFormTest(TestCase):
    def test_registration_saves_names(self):
        resume = SimpleUploadedFile("resume.pdf", b"file_content", content_type="application/pdf")
        data = {
            'username': 'teststudent',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '1234567890',
            'college': 'Test University',
            'degree': 'B.Tech',
            'cgpa': 9.5,
            'skills': 'Python, Django',
        }
        files = {'resume': resume}
        form = StudentRegistrationForm(data=data, files=files)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ApplicationSignalTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', email='student@test.com')
        self.student = Student.objects.create(user=self.user, cgpa=9.0)
        self.company = Company.objects.create(name="Test Corp")
        self.internship = Internship.objects.create(
            company=self.company, title="Internship", stipend=1000, 
            openings=1, last_date=datetime.date.today()
        )
        self.application = Application.objects.create(
            student=self.student, internship=self.internship, status='Applied'
        )

    def test_email_sent_on_status_change(self):
        # Clear outbox
        mail.outbox = []
        
        # Update status
        self.application.status = 'Selected'
        self.application.save()
        
        # Check email
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Application Status: Selected", mail.outbox[0].subject)

    def test_no_email_sent_on_other_update(self):
        # Clear outbox
        mail.outbox = []
        
        # Update something else
        self.application.admin_remarks = "Checking profile"
        self.application.save()
        
        # Check email - should NOT be sent because status didn't change
        self.assertEqual(len(mail.outbox), 0)
