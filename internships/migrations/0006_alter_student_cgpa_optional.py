# Generated migration — make Student.cgpa optional (blank=True, null=True)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internships', '0005_make_internship_fields_optional'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='cgpa',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True),
        ),
    ]
