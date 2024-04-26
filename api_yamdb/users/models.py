from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string


class MyUser(AbstractUser):
    """Пользовательская модель."""

    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Role', max_length=50,
        choices=[('user', 'User'), ('moderator', 'Moderator'),
                 ('admin', 'Admin')])
    confirmation_code = models.CharField('Confirmation Code',
                                         max_length=20, blank=True)

    def generate_confirmation_code(self):
        self.confirmation_code = get_random_string(length=20)
        self.save()
        return self.confirmation_code

    def check_confirmation_code(self, code):
        return self.confirmation_code == code
