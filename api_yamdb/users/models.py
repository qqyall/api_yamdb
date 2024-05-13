from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string

from api.constants import LEN_CODE_USER, MAX_LEN_CODE_USER, MAX_LEN_ROLE_USER


class User(AbstractUser):
    """Пользовательская модель."""
    USER: str = 'user'
    MODERATOR: str = 'moderator'
    ADMIN: str = 'admin'
    CHOICES: list[str] = (
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Admin'),
    )

    bio = models.TextField('Биография', blank=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    role = models.CharField(
        'Role', max_length=MAX_LEN_ROLE_USER,
        choices=CHOICES, default='user')
    confirmation_code = models.CharField(
        'Confirmation Code', max_length=MAX_LEN_CODE_USER, blank=True
    )

    class Meta:
        ordering = ('id',)

    def generate_confirmation_code(self):
        self.confirmation_code = get_random_string(length=LEN_CODE_USER)
        self.save()
        return self.confirmation_code

    def check_confirmation_code(self, code):
        return self.confirmation_code == code

    @property
    def is_admin(self):
        return self.role == User.ADMIN or self.is_super_user

    @property
    def is_moderator(self):
        return self.role == User.MODERATOR

    @property
    def is_user(self):
        return self.role == User.USER

    @property
    def is_super_user(self):
        return self.is_superuser
