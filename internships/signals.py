from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Application

@receiver(pre_save, sender=Application)
def notify_status_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Application.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                subject = f"[Internship Founder] Application Status: {instance.status}"
                message = (
                    f"Hello {instance.student.user.username},\n\n"
                    f"Your application for '{instance.internship.title}' at "
                    f"'{instance.internship.company.name}' has been updated.\n\n"
                    f"Status: {instance.status}\n"
                    f"Remarks: {instance.admin_remarks or 'No remarks.'}\n\n"
                    f"Best of luck!\n— Internship Founder Team"
                )
                send_mail(
                    subject,
                    message,
                    'noreply@internflow.com',
                    [instance.student.user.email],
                    fail_silently=True,
                )
        except Application.DoesNotExist:
            pass
