# Generated by Django 3.1.7 on 2021-05-17 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0003_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='isdelete',
            field=models.BooleanField(default=False),
        ),
    ]
