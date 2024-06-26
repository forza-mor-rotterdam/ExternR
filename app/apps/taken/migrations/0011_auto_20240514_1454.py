# Generated by Django 3.2.18 on 2024-05-14 12:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("taken", "0010_auto_20240314_1003"),
    ]

    operations = [
        migrations.AddField(
            model_name="taaktype",
            name="externe_instantie_email",
            field=models.EmailField(default="jippiejorrit@gmail.com", max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="taaktype",
            name="externe_instantie_feedback_vereist",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="taaktype",
            name="externe_instantie_naam",
            field=models.CharField(default="ext", max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="taaktype",
            name="externe_instantie_naam_verantwoordelijke",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
