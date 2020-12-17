# Generated by Django 3.1.2 on 2020-11-03 22:47

import django.db.models.manager
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('web_app', '0002_auto_20201029_1224'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='subscription',
            managers=[
                ('subscriptionTypes', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='subscription',
            name='name',
            field=models.CharField(default=None, max_length=20),
        ),
    ]