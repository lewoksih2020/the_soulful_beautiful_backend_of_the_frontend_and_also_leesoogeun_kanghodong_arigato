# Generated by Django 2.2.2 on 2020-08-02 04:40

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_bleach.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('subs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Savingrequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('title', django_bleach.models.BleachField(validators=[django.core.validators.MaxLengthValidator(150, message='The title can only be 150 characters in length.')])),
                ('savingamount', models.IntegerField()),
                ('body', django_bleach.models.BleachField(blank=True)),
                ('authorsender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='savingrequests', to=settings.AUTH_USER_MODEL)),
                ('subreddit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='savingrequests', to='subs.Sub')),
            ],
        ),
    ]
