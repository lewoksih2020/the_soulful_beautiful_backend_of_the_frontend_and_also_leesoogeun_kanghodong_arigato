# Generated by Django 2.2.2 on 2020-07-30 12:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('subs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('loanrequests', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanrequest',
            name='authorsender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='loanrequests', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='loanrequest',
            name='subreddit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loanrequests', to='subs.Sub'),
        ),
    ]
