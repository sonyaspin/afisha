from django.db import models


class SiteSettings(models.Model):
    company_name = models.CharField('Название', max_length=100, default='IT_COMPANY')
    tagline = models.CharField('Подзаголовок', max_length=200, default='разработка · инфраструктура')
    hero_line1 = models.CharField('Заголовок 1', max_length=100, default='Строим цифровые')
    hero_line2 = models.CharField('Заголовок 2', max_length=100, default='продукты для')
    hero_line3 = models.CharField('Заголовок 3', max_length=100, default='бизнеса')
    hero_text = models.TextField(
        'Текст справа',
        default='Небольшая команда. Фокус на качестве, а не на количестве проектов. Работаем с компаниями, которым важна надёжность.'
    )
    footer_text = models.CharField('Низ', max_length=200, default='© 2026 IT_COMPANY')

    class Meta:
        verbose_name = 'Шапка сайта'
        verbose_name_plural = 'Шапка сайта'

    def __str__(self):
        return 'Настройки'


class Stat(models.Model):
    value = models.CharField('Значение', max_length=50)
    label = models.CharField('Подпись', max_length=200)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Цифра'
        verbose_name_plural = 'Цифры'
        ordering = ['order']

    def __str__(self):
        return self.value


class Service(models.Model):
    number = models.CharField('Номер', max_length=10, default='01')
    title = models.CharField('Название', max_length=100)
    description = models.TextField('Описание')
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Направления'
        verbose_name_plural = 'Направления'
        ordering = ['order']

    def __str__(self):
        return self.title


class ProcessStep(models.Model):
    number = models.CharField('Номер', max_length=10, default='01')
    title = models.CharField('Название', max_length=100)
    description = models.TextField('Описание')
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Шаги процесса'
        verbose_name_plural = 'Шаги процесса'
        ordering = ['order']

    def __str__(self):
        return self.title


class InfoCard(models.Model):
    title = models.CharField('Заголовок', max_length=100)
    description = models.TextField('Описание')
    button_text = models.CharField('Кнопка', max_length=100, default='Подробнее →')
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Карточка'
        verbose_name_plural = 'Карточки'
        ordering = ['order']

    def __str__(self):
        return self.title


class ContactItem(models.Model):
    title = models.CharField('Заголовок', max_length=100)
    main_text = models.CharField('Текст', max_length=200)
    extra_text = models.CharField('Доп. текст', max_length=200, blank=True)
    note = models.CharField('Подпись', max_length=200, blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'
        ordering = ['order']

    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField('Название', max_length=200)
    category = models.CharField('Категория', max_length=50)
    date = models.DateField('Дата')
    time = models.TimeField('Время')
    place = models.CharField('Место', max_length=200)
    address = models.CharField('Адрес', max_length=200)
    price = models.CharField('Цена', max_length=100)
    image_file = models.ImageField('Фото (загрузить с компьютера)', upload_to='events/', blank=True)
    image = models.URLField('Или ссылка на картинку', blank=True)
    tag = models.CharField('Тег', max_length=50, blank=True)
    description = models.TextField('Описание', blank=True)
    is_favorite = models.BooleanField('В избранном (подборка редакции)', default=False)

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'
        ordering = ['date', 'time']

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        if self.image_file:
            return self.image_file.url
        return self.image


class Movie(models.Model):
    title = models.CharField('Название', max_length=200)
    age = models.CharField('Возраст', max_length=10)
    premiere = models.BooleanField('Премьера', default=False)
    cinema = models.CharField('Кинотеатр', max_length=200)
    times = models.CharField('Сеансы (старый текстовый способ)', max_length=200, blank=True)
    price = models.CharField('Цена', max_length=100)
    image_file = models.ImageField('Постер (загрузить с компьютера)', upload_to='movies/', blank=True)
    image = models.URLField('Или ссылка на постер', blank=True)
    genre = models.CharField('Жанр', max_length=100, blank=True)
    year = models.PositiveSmallIntegerField('Год', null=True, blank=True)
    duration = models.PositiveSmallIntegerField('Длительность (минут)', null=True, blank=True)
    country = models.CharField('Страна', max_length=100, blank=True)
    lead = models.CharField('Краткое описание', max_length=300, blank=True)
    description = models.TextField('Полное описание', blank=True)
    is_favorite = models.BooleanField('В избранном (подборка редакции)', default=False)

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        if self.image_file:
            return self.image_file.url
        return self.image

    def times_list(self):
        times = [s.time.strftime('%H:%M') for s in self.sessions.all()]
        if times:
            return times
        return [t.strip() for t in self.times.split(',') if t.strip()]


class Actor(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='actors', verbose_name='Фильм')
    name = models.CharField('Имя', max_length=100)
    role = models.CharField('Роль', max_length=100, blank=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)
    is_favorite = models.BooleanField('В избранном (подборка редакции)', default=False)

    class Meta:
        verbose_name = 'Актёр'
        verbose_name_plural = 'Актёры'
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='sessions', verbose_name='Фильм')
    time = models.TimeField('Время')
    format = models.CharField('Формат', max_length=20, default='2D', blank=True)
    price = models.CharField('Цена (если отличается от общей)', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Сеанс'
        verbose_name_plural = 'Сеансы'
        ordering = ['time']

    def __str__(self):
        return self.time.strftime('%H:%M')


class TourPlace(models.Model):
    name = models.CharField('Название места', max_length=200)
    region = models.CharField('Район', max_length=100, blank=True, help_text='Например: Чегемский район')
    distance_km = models.PositiveSmallIntegerField('Расстояние от Нальчика, км', null=True, blank=True)
    travel_time = models.CharField('Время в пути', max_length=100, blank=True,
                                   help_text='Например: ~1 час на машине')
    description = models.TextField('Описание', blank=True)
    tags = models.CharField('Теги', max_length=200, blank=True,
                            help_text='Через запятую: водопад, горы, легко добраться')
    map_url = models.URLField('Ссылка на Яндекс.Карты', max_length=500, blank=True,
                              help_text='Скопируйте ссылку из Яндекс.Карт (кнопка «Поделиться»). Если пусто — ссылка на поиск по названию места')
    image_file = models.ImageField('Фото (загрузить с компьютера)', upload_to='tourism/places/', blank=True)
    image = models.URLField('Или ссылка на фото', blank=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0, help_text='Меньше число — выше в списке')
    date_start = models.DateField('Дата (или дата начала)', null=True, blank=True)
    date_end = models.DateField('Дата окончания', null=True, blank=True,
                                help_text='Если событие длится несколько дней. Для одного дня оставьте пустым')
    time_start = models.TimeField('Время начала', null=True, blank=True)
    time_end = models.TimeField('Время окончания', null=True, blank=True)
    is_favorite = models.BooleanField('В избранном (подборка редакции)', default=False)

    class Meta:
        verbose_name = 'Туристическое место'
        verbose_name_plural = 'Туристические места'
        ordering = ['order', 'id']

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        return self.image_file.url if self.image_file else self.image

    @property
    def tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    @property
    def location_line(self):
        parts = []
        if self.region:
            parts.append(self.region)
        if self.distance_km is not None:
            parts.append('%s км от Нальчика' % self.distance_km)
        if self.travel_time:
            parts.append(self.travel_time)
        return ' · '.join(parts)

    @property
    def map_link(self):
        if self.map_url:
            return self.map_url
        from urllib.parse import quote
        return 'https://yandex.ru/maps/?text=' + quote('%s, Кабардино-Балкария' % self.name)


class Guide(models.Model):
    name = models.CharField('Имя', max_length=150)
    image_file = models.ImageField('Фото (загрузить с компьютера)', upload_to='tourism/guides/', blank=True)
    image = models.URLField('Или ссылка на фото', blank=True)
    rating = models.DecimalField('Рейтинг', max_digits=3, decimal_places=2, default=5.00)
    reviews_count = models.PositiveIntegerField('Количество отзывов', default=0)
    specialization = models.CharField('Специализация', max_length=200, blank=True,
                                      help_text='Например: гид по горным ущельям')
    languages = models.CharField('Языки', max_length=100, blank=True, help_text='Через запятую: русский, английский')
    bio = models.TextField('О гиде', blank=True)
    contact_url = models.URLField('Ссылка для связи', blank=True, help_text='Telegram, WhatsApp, сайт — куда ведёт «Написать гиду»')
    order = models.PositiveSmallIntegerField('Порядок', default=0, help_text='Меньше число — выше в списке')
    is_favorite = models.BooleanField('В избранном (подборка редакции)', default=False)

    class Meta:
        verbose_name = 'Гид'
        verbose_name_plural = 'Гиды'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        return self.image_file.url if self.image_file else self.image

    @property
    def languages_list(self):
        return [t.strip() for t in self.languages.split(',') if t.strip()]


class Tour(models.Model):
    KIND_CHOICES = [
        ('excursion', 'Экскурсия'),
        ('hike', 'Поход и треккинг'),
        ('tour', 'Тур (многодневный)'),
        ('other', 'Другое'),
    ]
    FORMAT_CHOICES = [
        ('individual', 'Индивидуальная'),
        ('group', 'Групповая'),
        ('mini', 'Мини-группа'),
    ]
    DURATION_CHOICES = [
        ('short', '2–4 часа'),
        ('half', 'Полдня'),
        ('day', 'Целый день'),
        ('multi', 'Многодневный'),
    ]
    DIFFICULTY_CHOICES = [
        ('easy', 'Лёгкий'),
        ('medium', 'Средний'),
        ('hard', 'Сложный'),
    ]
    OTHER_CHOICES = [
        ('bike', 'Вело'),
        ('photo', 'Фото'),
        ('food', 'Еда'),
        ('jeep', 'Джиппинг'),
        ('gear', 'Снаряжение'),
    ]

    title = models.CharField('Название', max_length=200)
    kind = models.CharField('Тип (вкладка на сайте)', max_length=10, choices=KIND_CHOICES, default='excursion')
    is_active = models.BooleanField('Показывать на сайте', default=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0, help_text='Меньше число — выше в списке')
    is_favorite = models.BooleanField('В избранном (подборка редакции)', default=False)

    image_file = models.ImageField('Фото (загрузить с компьютера)', upload_to='tourism/tours/', blank=True)
    image = models.URLField('Или ссылка на фото', blank=True)

    duration_group = models.CharField('Длительность (для фильтра)', max_length=10,
                                      choices=DURATION_CHOICES, default='day')
    duration_text = models.CharField('Длительность (текст в карточке)', max_length=50, blank=True,
                                     help_text='Например: 8 часов  или  3 дня / 2 ночи')
    format = models.CharField('Формат', max_length=12, choices=FORMAT_CHOICES, default='group')
    transport = models.CharField('Как передвигаемся', max_length=50, blank=True,
                                 help_text='Например: на машине, пешком, велосипед')
    max_people = models.PositiveSmallIntegerField('Максимум человек', null=True, blank=True)
    distance_km = models.PositiveSmallIntegerField('Длина маршрута, км (для походов)', null=True, blank=True)
    difficulty = models.CharField('Сложность (для походов)', max_length=10, choices=DIFFICULTY_CHOICES, blank=True)
    other_type = models.CharField('Вид (для вкладки «Другое»)', max_length=10, choices=OTHER_CHOICES, blank=True)

    price = models.PositiveIntegerField('Цена, ₽', default=0, help_text='Только число, например 3500')
    price_unit = models.CharField('Подпись к цене', max_length=20, default='₽/чел', blank=True,
                                  help_text='Например: ₽/чел  или  ₽')

    date_start = models.DateField('Дата (или дата начала)', null=True, blank=True)
    date_end = models.DateField('Дата окончания', null=True, blank=True,
                                help_text='Если событие длится несколько дней. Для одного дня оставьте пустым')
    time_start = models.TimeField('Время начала', null=True, blank=True)
    time_end = models.TimeField('Время окончания', null=True, blank=True)

    description = models.TextField('Короткое описание', blank=True,
                                   help_text='Для экскурсий, походов и «Другое» — 2–3 строки. Для походов: что увидите и что взять с собой')
    program = models.TextField('Маршрут по дням и что включено', blank=True, help_text='Только для туров')

    guide = models.ForeignKey(Guide, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='tours', verbose_name='Гид')
    places = models.ManyToManyField(TourPlace, blank=True, related_name='tours', verbose_name='Места')

    button_text = models.CharField('Текст кнопки', max_length=30, blank=True,
                                   help_text='Пусто = «Забронировать» (для походов «Записаться»)')
    booking_url = models.URLField('Ссылка для бронирования', blank=True)

    class Meta:
        verbose_name = 'Экскурсия / тур'
        verbose_name_plural = 'Экскурсии, походы, туры'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        return self.image_file.url if self.image_file else self.image

    @property
    def price_group(self):
        if self.price <= 3000:
            return 'p1'
        if self.price <= 10000:
            return 'p2'
        return 'p3'

    @property
    def price_label(self):
        num = '{:,}'.format(self.price).replace(',', '\u00a0')
        return ('%s %s' % (num, self.price_unit)).strip()

    @property
    def badge(self):
        if self.kind == 'excursion':
            return self.get_format_display()
        if self.kind == 'hike':
            return 'Поход'
        if self.kind == 'tour':
            return 'Многодневный'
        return self.get_other_type_display() or 'Другое'

    @property
    def difficulty_label(self):
        return self.get_difficulty_display().lower() if self.difficulty else ''

    @property
    def facts(self):
        f = []
        if self.duration_text:
            f.append(self.duration_text)
        if self.kind == 'tour':
            grp = {'individual': 'индивидуально', 'group': 'группа', 'mini': 'мини-группа'}[self.format]
            f.append('%s до %s' % (grp, self.max_people) if self.max_people else grp)
            if self.transport:
                f.append(self.transport)
        else:
            if self.transport:
                f.append(self.transport)
            if self.kind == 'hike':
                if self.distance_km:
                    f.append('%s км' % self.distance_km)
                if self.difficulty:
                    f.append({'easy': 'лёгкая', 'medium': 'средняя', 'hard': 'высокая'}[self.difficulty] + ' сложность')
            elif self.max_people:
                f.append(('группа до %s' if self.kind == 'other' else 'до %s человек') % self.max_people)
        return f

    @property
    def button_label(self):
        if self.button_text:
            return self.button_text
        return 'Записаться' if self.kind == 'hike' else 'Забронировать'

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.date_end and not self.date_start:
            raise ValidationError({'date_start': 'Укажите дату начала.'})
        if self.date_end and self.date_start and self.date_end < self.date_start:
            raise ValidationError({'date_end': 'Дата окончания раньше даты начала.'})

    @property
    def when_label(self):
        from django.utils import timezone
        months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля',
                  'августа', 'сентября', 'октября', 'ноября', 'декабря']
        year = timezone.localdate().year
        parts = []
        d1, d2 = self.date_start, self.date_end
        if d1:
            if d2 and d2 != d1:
                if d1.year == d2.year and d1.month == d2.month:
                    s = '%d–%d %s' % (d1.day, d2.day, months[d1.month - 1])
                else:
                    s = '%d %s – %d %s' % (d1.day, months[d1.month - 1], d2.day, months[d2.month - 1])
                if d1.year != d2.year:
                    s = '%d %s %d – %d %s %d' % (d1.day, months[d1.month - 1], d1.year, d2.day, months[d2.month - 1], d2.year)
                elif d2.year != year:
                    s += ' %d' % d2.year
            else:
                s = '%d %s' % (d1.day, months[d1.month - 1])
                if d1.year != year:
                    s += ' %d' % d1.year
            parts.append(s)
        if self.time_start:
            t = self.time_start.strftime('%H:%M')
            if self.time_end:
                t += '–' + self.time_end.strftime('%H:%M')
            parts.append(t)
        return ', '.join(parts)

from .accounts import Profile, Favorite  # noqa: E402,F401
