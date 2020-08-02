from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

from subs.models import Sub

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class MyUserManager(BaseUserManager):
    def create_user(self, email, username, location, first_name, savingtarget, aadharcard, last_name, age,
                    password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        if not location:
            raise ValueError('Users must have a location')

        if not first_name:
            raise ValueError('Users must have a first_name')

        if not savingtarget:
            raise ValueError('Users must have a savingtarget')

        if not last_name:
            raise ValueError('Users must have a last_name')

        if not age:
            raise ValueError('Users must have a age')

        if not aadharcard:
            raise ValueError('Users must have a aadharcard')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            location=location,
            first_name=first_name,
            savingtarget=savingtarget,
            aadharcard=aadharcard,
            last_name=last_name,
            age=age,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, location, first_name, savingtarget, aadharcard, last_name, age, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
            location=location,
            first_name=first_name,
            savingtarget=savingtarget,
            aadharcard=aadharcard,
            last_name=last_name,
            age=age,

        )
        user.is_admin = True
        user.is_verified_aadharcard = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    karma = models.IntegerField(default=0)
    subs = models.ManyToManyField(
        Sub,
        through='UserSubMembership',
        related_name='members',

    )
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    location = models.CharField(max_length=60, unique=False)
    first_name = models.CharField(max_length=60, unique=False)
    savingtarget = models.IntegerField(default=1000)
    aadharcard = models.CharField(max_length=60, unique=True)
    last_name = models.CharField(max_length=60, unique=False)
    age = models.IntegerField(max_length=2, unique=False)
    dummySubResponse = models.CharField(max_length=100)
    dummyAccountField = models.CharField(max_length=100)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_verified_aadharcard = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # USERNAME_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'location', 'first_name', 'savingtarget', 'aadharcard', 'last_name', 'age']
    # REQUIRED_FIELDS = ['username']

    objects = MyUserManager()

    def __str__(self):
        return self.email

    # For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


# class User(AbstractUser):
# karma = models.IntegerField(default=0)
# subs = models.ManyToManyField(
#     Sub,
#     through='UserSubMembership',
#     related_name='members',
#
# )
# email = models.EmailField(unique=True)
# ManyToManyField on Subreddit, related_name="moderated_subs"
# ManyToManyField for votes on Comment, related_name="voted_comments"
# ManyToManyField for votes on Post, related_name="voted_posts"
# Reverse FK for user votes on PostVote, related_name="post_votes"
# Reverse FK for user votes on CommentVote, related_name="comment_votes"
# Reverse FK to Comment related_name="comments"
# Reverse FK to Post related_name="loanrequests"


class UserSubMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sub = models.ForeignKey(Sub, on_delete=models.CASCADE)
    sign_up_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'sub')
