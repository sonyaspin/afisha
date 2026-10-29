#!/bin/bash
# Запуск на сервере из /var/www/landing:   bash check_install.sh
# Показывает, какие файлы остались СТАРЫМИ (с «зашитой» Алиной или без защиты кабинета).
cd /var/www/landing || exit 1
echo "=== 1. Где в шаблонах осталась зашитая Алина (должно быть пусто) ==="
grep -rln "Алина\|Хасанова\|alina@example" landing/templates/ || echo "  ок, ничего нет"
echo
echo "=== 2. Защита страниц кабинета (должно быть 3 строки в views.py и 1 в auth_views.py) ==="
grep -c "@login_required" landing/views.py landing/auth_views.py 2>&1
echo
echo "=== 3. Настройки (должны быть найдены обе строки) ==="
grep -n "LOGIN_URL\|auth_profile" mysite/settings.py || echo "  НЕ НАЙДЕНО: добавьте по инструкции НАСТРОЙКА_settings_и_models.txt"
echo
echo "=== 4. Адреса (должны быть auth/login, auth/register, cabinet/tourism, favorites/toggle) ==="
grep -n "auth/login\|auth/register\|cabinet/tourism\|favorites/toggle" landing/urls.py || echo "  НЕ НАЙДЕНО: urls.py старый"
echo
echo "=== 5. Какие шаблоны кабинета новые (должны содержать _lk_avatar) ==="
grep -L "_lk_avatar" landing/templates/landing/cabinet_*.html || echo "  ок, во всех четырёх"
