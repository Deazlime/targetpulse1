# Generated by Django 4.2 on 2025-05-16 17:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('targetpulse', '0006_remove_timeentry_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='targetpulse.task'),
        ),
    ]
