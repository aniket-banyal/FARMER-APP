# Generated by Django 3.2.9 on 2022-09-15 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_cartitem_num_of_days_cartitem_rent'),
    ]

    operations = [
        migrations.CreateModel(
            name='Machine_models',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('image1', models.ImageField(upload_to='machine_model_images/')),
                ('image2', models.ImageField(upload_to='machine_model_images/')),
            ],
        ),
    ]