import random
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, phone_number=None, is_verified=False):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            phone_number=phone_number,
            is_verified=is_verified
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, phone_number=None):
        user = self.create_user(
            username=username,
            email=email,
            password=password,
            phone_number=phone_number,
            is_verified=True  # Superusers should be verified by default
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user


class Users(AbstractBaseUser, PermissionsMixin):

    user_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    username = models.CharField(max_length=255, unique=False, null=True, blank=True)
    email = models.EmailField(unique=True, max_length=255)
    phone_number = models.CharField(max_length=11, unique=True, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(default=timezone.now)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    groups = models.ManyToManyField(Group, related_name='custom_user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions')

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'users'


class Profile(models.Model):
    user_id = models.OneToOneField(Users, on_delete=models.CASCADE, primary_key=True)
    profile_picture = models.ImageField(upload_to=f'uploads/profile_picture/{user_id}/', null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)
    phone_number = models.CharField(max_length=11, null=True, blank=True)


class BaseToken(models.Model):
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    token = models.CharField(max_length=5, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    class Meta:
        abstract = True  # Makes this model abstract, so it won't create a separate table
        indexes = [
            models.Index(fields=['created_at', 'expires_at']),
        ]

    def save(self, *args, **kwargs):
        # Generate token and set expiration if it's a new token or the existing one is expired
        if not self.token or self.is_expired():
            self.token = self._generate_token()
            self.created_at = timezone.now()
            self.expires_at = self.created_at + timezone.timedelta(minutes=10)

        if len(self.token) != 4:
            raise ValidationError("Token must be 5 characters.")

        super().save(*args, **kwargs)

    def _generate_token(self):

        while True:
            token = f"{random.randint(1000, 9999)}"

            if not (AccountVerificationToken.objects.filter(token=token).exists() or
                    ResetPasswordToken.objects.filter(token=token).exists()):
                return token

    def is_expired(self):
        """ Check if the token has expired """
        return timezone.now() > self.expires_at


class ResetPasswordToken(BaseToken):
    class Meta:
        db_table = 'reset_password_tokens'


class AccountVerificationToken(BaseToken):
    class Meta:
        db_table = 'account_verification_tokens'
