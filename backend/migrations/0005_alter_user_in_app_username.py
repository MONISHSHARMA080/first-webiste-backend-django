# Generated by Django 3.2.22 on 2024-04-13 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_auto_20240413_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_in_app',
            name='username',
            field=models.CharField(max_length=700, unique=True),
        ),
    ]
