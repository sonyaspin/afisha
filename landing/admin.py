# landing/admin.py — ПОЛНАЯ замена файла.
# Event, Movie, Actor, Session — как в прошлой версии; добавлены TourPlace, Guide, Tour.
from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from .models import Event, Movie, Actor, Session, TourPlace, Guide, Tour, Profile, Favorite


class PreviewMixin:
    def preview(self, obj):
        url = obj.image_url if obj.pk else ''
        if not url:
            return '—'
        return format_html('<img src="{}" style="height:90px;border-radius:10px;object-fit:cover;">', url)
    preview.short_description = 'Превью'


# ---------------- Афиша и кино ----------------
@admin.register(Event)
class EventAdmin(PreviewMixin, admin.ModelAdmin):
    list_display = ('preview', 'title', 'category', 'date', 'time', 'place')
    list_display_links = ('preview', 'title')
    list_filter = ('category', 'date')
    search_fields = ('title', 'place')
    readonly_fields = ('preview',)
    exclude = ('is_favorite',)


class ActorInline(admin.TabularInline):
    model = Actor
    extra = 3
    fields = ('name', 'role', 'order')


class SessionInline(admin.TabularInline):
    model = Session
    extra = 4
    fields = ('time', 'format', 'price')


@admin.register(Movie)
class MovieAdmin(PreviewMixin, admin.ModelAdmin):
    list_display = ('preview', 'title', 'age', 'cinema', 'premiere')
    list_display_links = ('preview', 'title')
    list_filter = ('premiere',)
    search_fields = ('title',)
    readonly_fields = ('preview',)
    exclude = ('times', 'is_favorite')
    inlines = [SessionInline, ActorInline]


# ---------------- Туризм ----------------
@admin.register(TourPlace)
class TourPlaceAdmin(PreviewMixin, admin.ModelAdmin):
    list_display = ('preview', 'name', 'place_location', 'tours_total', 'order')
    list_display_links = ('preview', 'name')
    list_editable = ('order',)
    search_fields = ('name', 'region', 'tags')
    readonly_fields = ('preview', 'related_tours')
    fieldsets = (
        ('Основное', {'fields': ('name', 'region', 'distance_km', 'travel_time', 'tags', 'map_url', 'order')}),
        ('Фото', {'fields': ('image_file', 'image', 'preview')}),
        ('Описание', {'fields': ('description',)}),
        ('Связанные экскурсии и туры (только просмотр)', {'fields': ('related_tours',)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_tours_total=Count('tours'))

    def place_location(self, obj):
        return obj.location_line or '—'
    place_location.short_description = 'Расположение'

    def tours_total(self, obj):
        return obj._tours_total
    tours_total.short_description = 'Предложений'
    tours_total.admin_order_field = '_tours_total'

    def related_tours(self, obj):
        if not obj.pk:
            return 'Появится после сохранения'
        items = [(reverse('admin:landing_tour_change', args=[t.pk]), t.title) for t in obj.tours.all()]
        if not items:
            return 'Пока нет экскурсий и туров, связанных с этим местом. Привязать место можно в карточке экскурсии/тура.'
        return format_html_join(mark_safe('<br>'), '<a href="{}">{}</a>', items)
    related_tours.short_description = 'Связанные экскурсии и туры'


class GuideTourInline(admin.TabularInline):
    model = Tour
    fk_name = 'guide'
    extra = 0
    max_num = 0
    can_delete = False
    show_change_link = True
    fields = ('title', 'kind', 'price', 'is_active')
    verbose_name = 'Экскурсия / тур гида'
    verbose_name_plural = 'Экскурсии и туры этого гида (новые добавляются в разделе «Экскурсии, походы, туры»)'


@admin.register(Guide)
class GuideAdmin(PreviewMixin, admin.ModelAdmin):
    list_display = ('preview', 'name', 'rating', 'reviews_count', 'specialization', 'order')
    list_display_links = ('preview', 'name')
    list_editable = ('order',)
    search_fields = ('name', 'specialization')
    readonly_fields = ('preview',)
    fieldsets = (
        ('Основное', {'fields': ('name', 'specialization', 'languages', 'order')}),
        ('Фото', {'fields': ('image_file', 'image', 'preview')}),
        ('Рейтинг', {'fields': ('rating', 'reviews_count')}),
        ('О гиде и связь', {'fields': ('bio', 'contact_url')}),
    )
    inlines = [GuideTourInline]


@admin.register(Tour)
class TourAdmin(PreviewMixin, admin.ModelAdmin):
    list_display = ('preview', 'title', 'kind', 'format', 'when_label', 'price', 'guide', 'is_active', 'order')
    list_display_links = ('preview', 'title')
    list_editable = ('is_active', 'order')
    list_filter = ('kind', 'format', 'difficulty', 'other_type', 'duration_group', 'is_active', 'guide')
    search_fields = ('title', 'description', 'guide__name', 'places__name')
    readonly_fields = ('preview',)
    autocomplete_fields = ('guide',)
    filter_horizontal = ('places',)
    fieldsets = (
        ('Основное', {'fields': ('title', 'kind', 'is_active', 'order')}),
        ('Фото', {'fields': ('image_file', 'image', 'preview')}),
        ('Дата и время', {'fields': ('date_start', 'date_end', 'time_start', 'time_end'),
                          'description': 'Дата — одна или период: для «10–20 октября» укажите дату начала и дату окончания. Если событие в один день, дату окончания оставьте пустой. Всё можно не заполнять — тогда дата в карточке не показывается.'}),
        ('Параметры', {'fields': ('duration_group', 'duration_text', 'format', 'transport', 'max_people'),
                       'description': 'Строка в карточке собирается из этих полей: длительность · как передвигаемся · сколько человек.'}),
        ('Только для походов', {'fields': ('distance_km', 'difficulty'), 'classes': ('collapse',)}),
        ('Только для вкладки «Другое»', {'fields': ('other_type',), 'classes': ('collapse',)}),
        ('Цена', {'fields': ('price', 'price_unit')}),
        ('Описание', {'fields': ('description', 'program')}),
        ('Гид и места', {'fields': ('guide', 'places')}),
        ('Кнопка', {'fields': ('button_text', 'booking_url')}),
    )

    def when_label(self, obj):
        return obj.when_label or '—'
    when_label.short_description = 'Когда'


# ---------------- Пользователи сайта ----------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_email', 'phone', 'city', 'created')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'phone', 'city')
    readonly_fields = ('created',)
    raw_id_fields = ('user',)

    def user_email(self, obj):
        return obj.user.email or '—'
    user_email.short_description = 'Email'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'kind', 'object_id', 'created')
    list_filter = ('kind',)
    search_fields = ('user__email', 'user__first_name')
    raw_id_fields = ('user',)
