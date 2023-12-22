# Generated by Django 4.2.7 on 2023-11-14 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("alpinism_app", "0003_remove_alpinist_name_remove_alpinist_surname_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="clubmembership",
            name="admin_confirmation",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="clubmembership",
            name="date_from",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]