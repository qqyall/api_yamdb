from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string

from api.constants import LEN_CODE_USER, MAX_LEN_CODE_USER, MAX_LEN_ROLE_USER


class User(AbstractUser):
    """Пользовательская модель."""

    bio = models.TextField('Биография', blank=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    role = models.CharField(
        'Role', max_length=MAX_LEN_ROLE_USER,
        choices=[('user', 'User'), ('moderator', 'Moderator'),
                 ('admin', 'Admin')], default='user')
    confirmation_code = models.CharField(
        'Confirmation Code', max_length=MAX_LEN_CODE_USER, blank=True
    )

    class Meta:
        ordering = ['id']

    def generate_confirmation_code(self):
        self.confirmation_code = get_random_string(length=LEN_CODE_USER)
        self.save()
        return self.confirmation_code

    def check_confirmation_code(self, code):
        return self.confirmation_code == code

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_user(self):
        return self.role == 'user'

    @property
    def is_super_user(self):
        return self.is_superuser
