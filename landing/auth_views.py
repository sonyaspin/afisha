# landing/auth_views.py — регистрация, вход, выход и настройки профиля
import datetime

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from .accounts import Favorite, Profile, get_profile, normalize_phone
from .models import Event, Guide, Movie, Tour, TourPlace

MAX_AVATAR = 2 * 1024 * 1024


def _next_url(request):
    nxt = request.POST.get('next') or ''
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return nxt
    return reverse('cabinet_tickets')


def _fail(errors, status=400):
    message = next(iter(errors.values()))
    return JsonResponse({'ok': False, 'errors': errors, 'message': message}, status=status)


@require_POST
def auth_register(request):
    name = (request.POST.get('name') or '').strip()
    email = (request.POST.get('email') or '').strip().lower()
    phone_raw = (request.POST.get('phone') or '').strip()
    p1 = request.POST.get('password') or ''
    p2 = request.POST.get('password2') or ''
    errors = {}

    if not name:
        errors['name'] = 'Укажите имя.'
    try:
        validate_email(email)
    except ValidationError:
        errors['email'] = 'Введите корректный email.'
    else:
        if User.objects.filter(Q(username__iexact=email) | Q(email__iexact=email)).exists():
            errors['email'] = 'Этот email уже зарегистрирован. Нажмите «Войти».'
    phone = normalize_phone(phone_raw)
    if phone_raw and not phone:
        errors['phone'] = 'Введите телефон в формате +7 928 123-45-67.'
    elif phone and Profile.objects.filter(phone=phone).exists():
        errors['phone'] = 'Этот номер уже используется.'
    if not p1:
        errors['password'] = 'Придумайте пароль.'
    else:
        try:
            validate_password(p1, user=User(username=email, email=email, first_name=name))
        except ValidationError as e:
            errors['password'] = ' '.join(e.messages)
    if p1 and p1 != p2:
        errors['password2'] = 'Пароли не совпадают.'
    if not request.POST.get('agree'):
        errors['agree'] = 'Нужно согласие с правилами.'
    if errors:
        return _fail(errors)

    parts = name.split(None, 1)
    try:
        user = User.objects.create_user(
            username=email, email=email, password=p1,
            first_name=parts[0][:150], last_name=(parts[1] if len(parts) > 1 else '')[:150])
    except IntegrityError:
        return _fail({'email': 'Этот email уже зарегистрирован. Нажмите «Войти».'})
    Profile.objects.create(user=user, phone=phone or None)
    login(request, user)
    return JsonResponse({'ok': True, 'redirect': _next_url(request)})


@require_POST
def auth_login(request):
    ident = (request.POST.get('login') or '').strip()
    password = request.POST.get('password') or ''
    if not ident or not password:
        return _fail({'login': 'Введите email или телефон и пароль.'})

    found = None
    if '@' in ident:
        found = User.objects.filter(Q(email__iexact=ident) | Q(username__iexact=ident)).first()
    else:
        phone = normalize_phone(ident)
        if phone:
            prof = Profile.objects.select_related('user').filter(phone=phone).first()
            found = prof.user if prof else None
        if found is None:
            found = User.objects.filter(username__iexact=ident).first()   # например, логин админа
    user = authenticate(request, username=found.get_username(), password=password) if found else None
    if user is None:
        return _fail({'login': 'Неверный логин или пароль.'})

    login(request, user)
    if not request.POST.get('remember'):
        request.session.set_expiry(0)          # не запоминать: сессия до закрытия браузера
    return JsonResponse({'ok': True, 'redirect': _next_url(request)})


@require_POST
def auth_logout(request):
    logout(request)
    return redirect('index')


@never_cache
@login_required
def cabinet_settings(request):
    user = request.user
    profile = get_profile(user)
    errors = {}
    saved = ''
    values = {
        'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email,
        'phone': profile.phone or '', 'city': profile.city,
        'birthday': profile.birthday.isoformat() if profile.birthday else '',
        'bio': profile.bio,
    }

    if request.method == 'POST':
        which = request.POST.get('form')

        if which == 'profile':
            for k in values:
                values[k] = (request.POST.get(k) or '').strip()
            values['email'] = values['email'].lower()

            if not values['first_name']:
                errors['first_name'] = 'Укажите имя.'
            try:
                validate_email(values['email'])
            except ValidationError:
                errors['email'] = 'Введите корректный email.'
            else:
                if User.objects.filter(Q(username__iexact=values['email']) | Q(email__iexact=values['email'])).exclude(pk=user.pk).exists():
                    errors['email'] = 'Этот email уже занят.'
            phone = normalize_phone(values['phone'])
            if values['phone'] and not phone:
                errors['phone'] = 'Введите телефон в формате +7 928 123-45-67.'
            elif phone and Profile.objects.filter(phone=phone).exclude(pk=profile.pk).exists():
                errors['phone'] = 'Этот номер уже используется.'
            birthday = None
            if values['birthday']:
                try:
                    birthday = datetime.date.fromisoformat(values['birthday'])
                    if birthday > datetime.date.today():
                        raise ValueError
                except ValueError:
                    errors['birthday'] = 'Проверьте дату рождения.'
            if len(values['bio']) > 500:
                errors['bio'] = 'Не больше 500 символов.'

            new_avatar = request.FILES.get('avatar')
            if new_avatar:
                if new_avatar.size > MAX_AVATAR:
                    errors['avatar'] = 'Файл больше 2 МБ.'
                else:
                    try:
                        from PIL import Image
                        Image.open(new_avatar).verify()
                        new_avatar.seek(0)
                    except Exception:
                        errors['avatar'] = 'Это не похоже на картинку (нужен PNG, JPG или WebP).'

            if not errors:
                user.first_name = values['first_name'][:150]
                user.last_name = values['last_name'][:150]
                user.email = values['email']
                user.username = values['email']
                user.save()
                profile.phone = phone or None
                profile.city = values['city'][:100]
                profile.birthday = birthday
                profile.bio = values['bio']
                if request.POST.get('remove_avatar') and profile.avatar:
                    profile.avatar.delete(save=False)
                if new_avatar:
                    if profile.avatar:
                        profile.avatar.delete(save=False)
                    profile.avatar = new_avatar
                profile.save()
                values['phone'] = profile.phone or ''
                saved = 'Изменения сохранены'

        elif which == 'password':
            old = request.POST.get('old_password') or ''
            new1 = request.POST.get('new_password') or ''
            new2 = request.POST.get('new_password2') or ''
            if not user.check_password(old):
                errors['old_password'] = 'Текущий пароль указан неверно.'
            if not new1:
                errors['new_password'] = 'Введите новый пароль.'
            else:
                try:
                    validate_password(new1, user=user)
                except ValidationError as e:
                    errors['new_password'] = ' '.join(e.messages)
            if new1 and new1 != new2:
                errors['new_password2'] = 'Пароли не совпадают.'
            if not errors:
                user.set_password(new1)
                user.save()
                update_session_auth_hash(request, user)     # остаёмся в аккаунте после смены пароля
                saved = 'Пароль изменён'

    return render(request, 'landing/cabinet_settings.html', {
        'values': values, 'errors': errors, 'saved': saved,
    })


FAV_MODELS = {'event': Event, 'movie': Movie, 'tour': Tour, 'place': TourPlace, 'guide': Guide}


@require_POST
def fav_toggle(request):
    """Добавить в избранное / убрать из избранного (для вошедшего пользователя)."""
    if not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'login': True,
                             'message': 'Войдите, чтобы сохранять в избранное.'}, status=401)
    model = FAV_MODELS.get(request.POST.get('kind'))
    try:
        oid = int(request.POST.get('id'))
    except (TypeError, ValueError):
        return JsonResponse({'ok': False, 'message': 'Некорректный запрос.'}, status=400)
    if model is None or not model.objects.filter(pk=oid).exists():
        return JsonResponse({'ok': False, 'message': 'Такого объекта нет.'}, status=404)
    fav, created = Favorite.objects.get_or_create(user=request.user, kind=request.POST['kind'], object_id=oid)
    if not created:
        fav.delete()
    return JsonResponse({'ok': True, 'on': created})
