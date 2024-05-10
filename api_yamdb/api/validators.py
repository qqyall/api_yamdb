from datetime import datetime

from django.core.exceptions import ValidationError


def year_validator(year):
    if year < 0:
        raise ValidationError('Значение года не может быть отрицательным')
    if year > datetime.datetime.now().year:
        raise ValidationError(
            ('Значение года не может быть больше текущего'),
        )
