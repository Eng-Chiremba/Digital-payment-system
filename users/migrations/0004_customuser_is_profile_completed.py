# Generated by Django 5.1.7 on 2025-04-02 22:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_customuser_date_of_birth_customuser_id_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_profile_completed',
            field=models.BooleanField(default=False),
        ),
    ]
