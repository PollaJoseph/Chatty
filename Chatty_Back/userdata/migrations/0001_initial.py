# Generated by Django 5.1 on 2024-11-02 15:50

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('username', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('user_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('phone_number', models.CharField(blank=True, max_length=11, null=True, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_verified', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(related_name='custom_user_groups', to='auth.group')),
                ('user_permissions', models.ManyToManyField(related_name='custom_user_permissions', to='auth.permission')),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.CreateModel(
            name='ResetPasswordToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=5, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('expires_at', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userdata.users')),
            ],
            options={
                'db_table': 'reset_password_tokens',
            },
        ),
        migrations.CreateModel(
            name='AccountVerificationToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=5, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('expires_at', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userdata.users')),
            ],
            options={
                'db_table': 'account_verification_tokens',
            },
        ),
    ]