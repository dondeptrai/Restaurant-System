# Generated by Django 5.1.2 on 2024-10-25 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="password",
            field=models.CharField(default="default_password", max_length=128),
        ),
    ]
