# Generated by Django 4.2.11 on 2024-11-14 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_cpuusagecontrol'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CpuUsageControl',
        ),
        migrations.AddField(
            model_name='containermetrics',
            name='cpu_usage_flag',
            field=models.BooleanField(default=False),
        ),
    ]
