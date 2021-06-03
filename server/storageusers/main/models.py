from django.db import models
from django.conf import settings
from django.core import validators
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager

import jwt
import random 
from datetime import datetime
from datetime import timedelta


class UserManager(BaseUserManager):

    def _create_user(self, username, password=None, name=None, isTeacher=False, **extra_fields):
        if not username:
            raise ValueError('Имя пользователя должно быть установлено')

        user = self.model(username=username, name=name, isTeacher=isTeacher, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, username, password=None, name=None, isTeacher=False, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(username, password, name, isTeacher, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self._create_user(username, password, **extra_fields)

    def get_user_from_token(self, token):
        _id = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return self.filter(id=_id['id'])


class MyUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(db_index=True, max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True)
    isTeacher = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = ()

    objects = UserManager()

    def __str__(self):
        return self.username

    @property
    def token(self):
        return self._generate_jwt_token()


    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.pk,
            'exp': int((dt-datetime(1970,1,1)).total_seconds())
        }, settings.SECRET_KEY, algorithm='HS256')
        # print(token)
        return token

class Content(models.Model):
    text = models.TextField(null=True, blank=True)
    