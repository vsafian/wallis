# Generated by Django 5.1.4 on 2025-02-05 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0003_remove_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('ready_to_print', 'Ready to Print'), ('in_progress', 'In Progress'), ('problem', 'Problem'), ('done', 'Done')], default='ready_to_print', max_length=50),
        ),
    ]
