# landing/urls.py — ПОЛНАЯ версия (замените файл целиком)
from django.urls import path
from . import views, auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('afisha/', views.afisha, name='afisha'),
    path('event/<int:event_id>/', views.event, name='event'),
    path('kino/', views.kino, name='kino'),
    # НОВОЕ:
    path('movie/<int:movie_id>/', views.movie, name='movie'),
    path('favorites/', views.favorites, name='favorites'),
    path('favorites/toggle/', auth_views.fav_toggle, name='fav_toggle'),
    path('suggest/', views.suggest, name='suggest'),
    path('suggest/tour/', views.suggest_tour, name='suggest_tour'),
    # Туризм:
    path('tourism/', views.tourism, name='tourism'),
    path('tourism/tour/<int:tour_id>/', views.tour_detail, name='tour_detail'),
    path('tourism/place/<int:place_id>/', views.place_detail, name='place_detail'),
    path('tourism/guide/<int:guide_id>/', views.guide_detail, name='guide_detail'),
    # Регистрация, вход, выход:
    path('auth/register/', auth_views.auth_register, name='auth_register'),
    path('auth/login/', auth_views.auth_login, name='auth_login'),
    path('auth/logout/', auth_views.auth_logout, name='logout'),
    # Личный кабинет:
    path('cabinet/tickets/', views.cabinet_tickets, name='cabinet_tickets'),
    path('cabinet/events/', views.cabinet_events, name='cabinet_events'),
    path('cabinet/tourism/', views.cabinet_tourism, name='cabinet_tourism'),
    path('cabinet/settings/', auth_views.cabinet_settings, name='cabinet_settings'),
]
