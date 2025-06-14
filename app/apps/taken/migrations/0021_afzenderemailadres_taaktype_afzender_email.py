# Generated by Django 4.2.15 on 2025-05-26 10:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("taken", "0020_taak_verwijderd_op"),
    ]

    operations = [
        migrations.CreateModel(
            name="AfzenderEmailadres",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name="taaktype",
            name="afzender_email",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="taken.afzenderemailadres",
            ),
        ),
    ]
