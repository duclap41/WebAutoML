# Generated by Django 5.0.6 on 2024-05-27 03:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0010_rename_conclusion_userfile_best_model_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userfile",
            name="data_file",
            field=models.FileField(upload_to="save_files/"),
        ),
    ]
