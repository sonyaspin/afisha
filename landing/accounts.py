# landing/accounts.py — профиль пользователя (дополнение к стандартному User из Django)
import re

from django.conf import settings
from django.db import models


def normalize_phone(raw):
    """Приводит телефон к виду +7XXXXXXXXXX. Если не похож на номер — возвращает ''."""
    digits = re.sub(r'\D', '', raw or '')
    if len(digits) == 11 and digits[0] in '78':
        return '+7' + digits[1:]
    if len(digits) == 10:
        return '+7' + digits
    return ''


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='profile', verbose_name='Пользователь')
    phone = models.CharField('Телефон', max_length=20, unique=True, null=True, blank=True,
                             help_text='В формате +79281234567')
    city = models.CharField('Город', max_length=100, blank=True)
    birthday = models.DateField('Дата рождения', null=True, blank=True)
    bio = models.TextField('О себе', blank=True, max_length=500)
    avatar = models.ImageField('Фото профиля', upload_to='avatars/', blank=True)
    created = models.DateTimeField('Дата регистрации', auto_now_add=True)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили пользователей'
        ordering = ['-created']

    def __str__(self):
        return self.user.get_full_name() or self.user.email or self.user.get_username()


class Favorite(models.Model):
    """Избранное пользователя: событие, фильм, экскурсия/тур, место или гид."""
    KINDS = [
        ('event', 'Событие'),
        ('movie', 'Фильм'),
        ('tour', 'Экскурсия / тур'),
        ('place', 'Туристическое место'),
        ('guide', 'Гид'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='favorites', verbose_name='Пользователь')
    kind = models.CharField('Что это', max_length=10, choices=KINDS)
    object_id = models.PositiveIntegerField('Номер (id)')
    created = models.DateTimeField('Когда добавлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное пользователей'
        ordering = ['-created']
        constraints = [models.UniqueConstraint(fields=['user', 'kind', 'object_id'], name='uniq_user_favorite')]

    def __str__(self):
        return '%s: %s #%s' % (self.user, self.get_kind_display(), self.object_id)


def get_profile(user):
    """Профиль есть у всех: у кого его нет (например, у админа) — создаётся пустой."""
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile
