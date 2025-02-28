# Generated by Django 5.1.4 on 2025-02-07 14:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0007_alter_order_status_alter_printqueue_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='printqueue',
            name='printer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='print_queues', to='production.printer'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('ready_to_print', 'Ready to Print'), ('in_progress', 'In Progress'), ('done', 'Done'), ('problem', 'Problem')], default='ready_to_print', max_length=50),
        ),
        migrations.AlterField(
            model_name='printqueue',
            name='status',
            field=models.CharField(choices=[('ready_to_print', 'Ready to Print'), ('in_progress', 'In Progress'), ('done', 'Done'), ('problem', 'Problem')], default='ready_to_print', max_length=50),
        ),
    ]
