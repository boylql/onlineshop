# Generated by Django 3.1.7 on 2021-04-01 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='pwd',
            field=models.CharField(max_length=60),
        ),
    ]
