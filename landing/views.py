# landing/views.py — ПОЛНАЯ версия (замените файл целиком)
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .accounts import Favorite
from .models import Event, Movie, TourPlace, Guide, Tour


def _days(n=14):
    """Даты для календарной ленты: сегодня + следующие n-1 дней."""
    today = timezone.localdate()
    return [today + timedelta(days=i) for i in range(n)]


def index(request):
    context = {
        'latest_events': Event.objects.all()[:3],
        'latest_movies': Movie.objects.prefetch_related('sessions')[:8],
        'events_count': Event.objects.count(),
        'days': _days(),
    }
    return render(request, 'landing/index.html', context)


def afisha(request):
    events = Event.objects.all()
    return render(request, 'landing/afisha.html', {
        'events': events,
        'free_count': events.filter(tag='Бесплатно').count(),
    })


def event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'landing/event.html', {'event': event})


def kino(request):
    movies = Movie.objects.prefetch_related('sessions')
    return render(request, 'landing/kino.html', {
        'movies': movies,
        'premieres_count': movies.filter(premiere=True).count(),
        'days': _days(),
    })


# ---------- НОВОЕ: добавьте в конец файла ----------
def movie(request, movie_id):
    movie = get_object_or_404(Movie.objects.prefetch_related('sessions', 'actors'), id=movie_id)
    return render(request, 'landing/movie.html', {'movie': movie})


def _with_tours():
    """Предзагрузка «показываемых» экскурсий для мест и гидов (атрибут active_tours)."""
    return Prefetch('tours', queryset=Tour.objects.filter(is_active=True), to_attr='active_tours')


@never_cache
def favorites(request):
    """Избранное — только то, что добавил сам вошедший пользователь."""
    ctx = {'events': [], 'movies': [], 'tours': [], 'places': [], 'guides': [], 'has_items': False}
    if request.user.is_authenticated:
        rows = list(Favorite.objects.filter(user=request.user).values_list('kind', 'object_id'))  # новые сверху

        def pick(kind, queryset):
            ids = [i for k, i in rows if k == kind]
            objs = {o.id: o for o in queryset.filter(id__in=ids)}
            return [objs[i] for i in ids if i in objs]

        active = Tour.objects.filter(is_active=True)
        ctx.update({
            'events': pick('event', Event.objects.all()),
            'movies': pick('movie', Movie.objects.prefetch_related('sessions')),
            'tours': pick('tour', active.select_related('guide').prefetch_related('places')),
            'places': pick('place', TourPlace.objects.prefetch_related(_with_tours())),
            'guides': pick('guide', Guide.objects.prefetch_related(_with_tours())),
        })
        ctx['has_items'] = any(ctx[k] for k in ('events', 'movies', 'tours', 'places', 'guides'))
    return render(request, 'landing/favorites.html', ctx)


def suggest(request):
    # Пока только визуал: форма никуда не отправляется.
    return render(request, 'landing/suggest.html')


# ---------- Личный кабинет (только для вошедших; настройки профиля — в auth_views.py) ----------
@never_cache
@login_required
def cabinet_tickets(request):
    return render(request, 'landing/cabinet_tickets.html')


@never_cache
@login_required
def cabinet_events(request):
    return render(request, 'landing/cabinet_events.html')


@never_cache
@login_required
def cabinet_tourism(request):
    return render(request, 'landing/cabinet_tourism.html')


# ---------- Туризм ----------
def tourism(request):
    active = Tour.objects.filter(is_active=True)
    by_kind = {'excursion': [], 'hike': [], 'tour': [], 'other': []}
    for t in active.select_related('guide').prefetch_related('places'):
        by_kind.setdefault(t.kind, []).append(t)

    # «С этим местом» / «Экскурсии гида»: только показываемые на сайте предложения
    place_tours = Prefetch('tours', queryset=active, to_attr='active_tours')
    guide_tours = Prefetch('tours', queryset=active, to_attr='active_tours')
    return render(request, 'landing/tourism.html', {
        'excursions': by_kind['excursion'],
        'hikes': by_kind['hike'],
        'tours': by_kind['tour'],
        'others': by_kind['other'],
        'guides': Guide.objects.prefetch_related(guide_tours),
        'places': TourPlace.objects.prefetch_related(place_tours),
        'offers_total': sum(len(v) for v in by_kind.values()),
    })


def suggest_tour(request):
    return render(request, 'landing/suggest_tour.html')


# ---------- Страницы «подробнее» ----------
def tour_detail(request, tour_id):
    tour = get_object_or_404(
        Tour.objects.select_related('guide').prefetch_related('places'),
        id=tour_id, is_active=True)
    related = (Tour.objects.filter(is_active=True, kind=tour.kind)
               .exclude(id=tour.id).select_related('guide').prefetch_related('places'))[:3]
    return render(request, 'landing/tour_detail.html', {'tour': tour, 'related': related})


def place_detail(request, place_id):
    place = get_object_or_404(TourPlace, id=place_id)
    tours = (place.tours.filter(is_active=True)
             .select_related('guide').prefetch_related('places'))
    return render(request, 'landing/place_detail.html', {'place': place, 'tours': tours})


def guide_detail(request, guide_id):
    guide = get_object_or_404(Guide, id=guide_id)
    tours = (guide.tours.filter(is_active=True)
             .select_related('guide').prefetch_related('places'))
    return render(request, 'landing/guide_detail.html', {'guide': guide, 'tours': tours})
