# Generated by Django 5.1.4 on 2025-02-05 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0005_alter_order_status_alter_printqueue_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('ready_to_print', 'Ready to Print'), ('in_progress', 'In Progress'), ('problem', 'Problem'), ('done', 'Done')], default='ready_to_print', max_length=50),
        ),
        migrations.AlterField(
            model_name='printqueue',
            name='status',
            field=models.CharField(choices=[('ready_to_print', 'Ready to Print'), ('in_progress', 'In Progress'), ('problem', 'Problem'), ('done', 'Done')], default='ready_to_print', max_length=50),
        ),
    ]
