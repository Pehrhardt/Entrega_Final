# Generated by Django 4.2.7 on 2023-11-20 19:16

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0006_post_imagen'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='now_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
