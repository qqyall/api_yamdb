from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    """Пользовательская модель."""

    bio = models.TextField('Биография', blank=True)
    # Подумать как заполнить role
    role = models.TextField()
