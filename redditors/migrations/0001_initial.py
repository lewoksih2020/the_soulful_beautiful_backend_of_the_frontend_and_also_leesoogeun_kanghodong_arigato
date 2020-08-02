# Generated by Django 2.2.2 on 2020-08-02 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('karma', models.IntegerField(default=0)),
                ('email', models.EmailField(max_length=60, unique=True, verbose_name='email')),
                ('username', models.CharField(max_length=30, unique=True)),
                ('location', models.CharField(max_length=60)),
                ('first_name', models.CharField(max_length=60)),
                ('savingtarget', models.IntegerField(default=1000)),
                ('aadharcard', models.CharField(max_length=60, unique=True)),
                ('last_name', models.CharField(max_length=60)),
                ('age', models.IntegerField(max_length=2)),
                ('dummySubResponse', models.CharField(max_length=100)),
                ('dummyAccountField', models.CharField(max_length=100)),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('last_login', models.DateTimeField(auto_now=True, verbose_name='last login')),
                ('is_admin', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserSubMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sign_up_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
