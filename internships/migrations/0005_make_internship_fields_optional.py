# Generated migration — make previously required Internship fields optional

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('internships', '0004_alter_company_description_alter_company_location_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='internship',
            name='company',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='internships',
                to='internships.company',
            ),
        ),
        migrations.AlterField(
            model_name='internship',
            name='title',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='internship',
            name='stipend',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='internship',
            name='mode',
            field=models.CharField(
                blank=True,
                choices=[('Remote', 'Remote'), ('Onsite', 'Onsite'), ('Hybrid', 'Hybrid')],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='internship',
            name='openings',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='internship',
            name='last_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
