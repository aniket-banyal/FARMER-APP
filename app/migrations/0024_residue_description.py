# Generated by Django 4.0.5 on 2022-07-15 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_residue_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='residue',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]