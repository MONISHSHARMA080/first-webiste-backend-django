# Generated by Django 3.2.22 on 2024-04-13 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user_in_app',
            options={},
        ),
        migrations.AddIndex(
            model_name='user_in_app',
            index=models.Index(fields=['registered_date', 'email', 'username'], name='backend_use_registe_913283_idx'),
        ),
        migrations.AddIndex(
            model_name='user_in_app',
            index=models.Index(fields=['email_verified', 'verified_through_auth_provider'], name='backend_use_email_v_53b634_idx'),
        ),
        migrations.AddIndex(
            model_name='user_in_app',
            index=models.Index(fields=['otp', 'otp_created_at'], name='backend_use_otp_9b38c0_idx'),
        ),
        migrations.AddIndex(
            model_name='user_in_app',
            index=models.Index(fields=['profile_picture_url', 'password'], name='backend_use_profile_cb892d_idx'),
        ),
    ]
