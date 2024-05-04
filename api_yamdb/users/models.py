from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string
from api.utils import MAX_LEN_ROLE_USER, MAX_LEN_CODE_USER, LEN_CODE_USER


class User(AbstractUser):
    """Пользовательская модель."""

    class Meta:
        ordering = ['id']

    bio = models.TextField('Биография', blank=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    role = models.CharField(
        'Role', max_length=MAX_LEN_ROLE_USER,
        choices=[('user', 'User'), ('moderator', 'Moderator'),
                 ('admin', 'Admin')], default='user')
    confirmation_code = models.CharField(
        'Confirmation Code', max_length=MAX_LEN_CODE_USER, blank=True
    )

    def generate_confirmation_code(self):
        self.confirmation_code = get_random_string(length=LEN_CODE_USER)
        self.save()
        return self.confirmation_code

    def check_confirmation_code(self, code):
        return self.confirmation_code == code

