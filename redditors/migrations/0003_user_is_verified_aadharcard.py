# Generated by Django 2.2.2 on 2020-08-02 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redditors', '0002_auto_20200802_1010'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_verified_aadharcard',
            field=models.BooleanField(default=False),
        ),
    ]
