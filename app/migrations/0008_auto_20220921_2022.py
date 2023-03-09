# Generated by Django 3.2.9 on 2022-09-21 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_machine_old_machine'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='machine',
            name='description',
        ),
        migrations.RemoveField(
            model_name='machine',
            name='details',
        ),
        migrations.AddField(
            model_name='machine_models',
            name='description',
            field=models.TextField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='machine_models',
            name='details',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
