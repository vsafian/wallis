# Generated by Django 5.1.4 on 2025-02-07 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0008_printqueue_printer_alter_order_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='printqueue',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('maintenance', 'Maintenance')], default='ready_to_print', max_length=50),
        ),
    ]
