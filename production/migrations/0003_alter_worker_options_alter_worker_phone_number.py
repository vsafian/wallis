# Generated by Django 5.1.4 on 2024-12-12 14:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0002_alter_worker_phone_number'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='worker',
            options={'ordering': ['-date_joined']},
        ),
        migrations.AlterField(
            model_name='worker',
            name='phone_number',
            field=models.CharField(blank=True, max_length=13, null=True, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_number', message='Phone number must be entered in the format: <+380999999999>!', regex='^\\+380\\d{9}$')]),
        ),
    ]
