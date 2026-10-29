# landing/tests.py — автоматическая проверка, что личный кабинет «у каждого свой» и закрыт от гостей.
# Запуск:  python manage.py test landing --settings=mysite.test_settings -v 2
import datetime
import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .accounts import Favorite
from .models import Event

CABINET = ['cabinet_tickets', 'cabinet_events', 'cabinet_tourism', 'cabinet_settings']
PASSWORD = 'Zx-91kLmPq!'


def make_user(email, name):
    return User.objects.create_user(username=email, email=email, password=PASSWORD, first_name=name)


class GuestTests(TestCase):
    def test_guest_cannot_open_cabinet_by_url(self):
        for name in CABINET:
            r = self.client.get(reverse(name))
            self.assertEqual(r.status_code, 302, name)
            self.assertIn('login=1', r['Location'], name)

    def test_guest_cannot_toggle_favorite(self):
        r = self.client.post(reverse('fav_toggle'), {'kind': 'event', 'id': 1})
        self.assertEqual(r.status_code, 401)

    def test_logout_needs_post(self):
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)

    def test_guest_favorites_page_is_not_personal(self):
        r = self.client.get(reverse('favorites'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Избранное доступно после входа')


class RegistrationTests(TestCase):
    def test_register_then_cabinet_is_empty_and_personal(self):
        r = self.client.post(reverse('auth_register'), {
            'name': 'Мадина Тестова', 'email': 'madina@example.com', 'phone': '+7 928 111-22-33',
            'password': PASSWORD, 'password2': PASSWORD, 'agree': 'on'})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(json.loads(r.content)['ok'])
        page = self.client.get(reverse('cabinet_tourism'))
        self.assertContains(page, 'Здравствуйте, Мадина!')
        settings_page = self.client.get(reverse('cabinet_settings'))
        self.assertContains(settings_page, 'madina@example.com')
        self.assertContains(settings_page, '+79281112233')

    def test_duplicate_email_rejected(self):
        make_user('a@example.com', 'Аня')
        r = self.client.post(reverse('auth_register'), {
            'name': 'Другая', 'email': 'A@example.com', 'password': PASSWORD, 'password2': PASSWORD, 'agree': 'on'})
        self.assertEqual(r.status_code, 400)

    def test_login_by_email_and_wrong_password(self):
        make_user('a@example.com', 'Аня')
        bad = self.client.post(reverse('auth_login'), {'login': 'a@example.com', 'password': 'nope'})
        self.assertEqual(bad.status_code, 400)
        good = self.client.post(reverse('auth_login'), {'login': 'a@example.com', 'password': PASSWORD})
        self.assertEqual(good.status_code, 200)


class IsolationTests(TestCase):
    def setUp(self):
        self.alina = make_user('alina@example.com', 'Алина')
        self.boris = make_user('boris@example.com', 'Борис')
        self.event = Event.objects.create(
            title='Тестовый концерт', category='Концерт', date=datetime.date(2030, 1, 1),
            time=datetime.time(19, 0), place='Зал', address='ул. Тестовая', price='500 ₽')

    def login(self, email):
        self.client.logout()
        self.assertTrue(self.client.login(username=email, password=PASSWORD))

    def test_each_user_sees_only_own_name(self):
        self.login('boris@example.com')
        for name in CABINET:
            r = self.client.get(reverse(name))
            self.assertContains(r, 'Здравствуйте, Борис!', msg_prefix=name)
            self.assertNotContains(r, 'Алина', msg_prefix=name)      # ничего «зашитого» в шаблонах нет
        self.login('alina@example.com')
        for name in CABINET:
            r = self.client.get(reverse(name))
            self.assertContains(r, 'Здравствуйте, Алина!', msg_prefix=name)
            self.assertNotContains(r, 'Борис', msg_prefix=name)

    def test_header_shows_name_on_public_pages(self):
        self.login('alina@example.com')
        for name in ('index', 'afisha', 'kino', 'tourism', 'favorites'):
            self.assertContains(self.client.get(reverse(name)), 'Алина', msg_prefix=name)

    def test_favorites_are_private(self):
        self.login('alina@example.com')
        r = self.client.post(reverse('fav_toggle'), {'kind': 'event', 'id': self.event.id})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(json.loads(r.content)['on'])
        self.assertContains(self.client.get(reverse('favorites')), 'Тестовый концерт')
        self.login('boris@example.com')
        self.assertNotContains(self.client.get(reverse('favorites')), 'Тестовый концерт')
        self.assertEqual(Favorite.objects.filter(user=self.boris).count(), 0)

    def test_toggle_twice_removes(self):
        self.login('alina@example.com')
        for _ in range(2):
            self.client.post(reverse('fav_toggle'), {'kind': 'event', 'id': self.event.id})
        self.assertEqual(Favorite.objects.filter(user=self.alina).count(), 0)

    def test_private_pages_are_not_cached(self):
        self.login('alina@example.com')
        for name in CABINET + ['favorites']:
            cc = self.client.get(reverse(name)).get('Cache-Control', '')
            self.assertIn('no-store', cc, name)

    def test_password_change_keeps_login(self):
        self.login('alina@example.com')
        r = self.client.post(reverse('cabinet_settings'), {
            'form': 'password', 'old_password': PASSWORD,
            'new_password': 'Qw-83hJkLp!', 'new_password2': 'Qw-83hJkLp!'})
        self.assertContains(r, 'Пароль изменён')
        self.assertEqual(self.client.get(reverse('cabinet_tickets')).status_code, 200)
