# Anti-cafe Booking Web App — актуальная карта проекта
Стек: Django 6.0.2 (монолит + Django templates) + Bootstrap 5 + PostgreSQL

Этот документ отражает фактическое состояние проекта в репозитории.

## 1) Приложения и ответственность
- `landing` — статичные страницы (TemplateView): главная, about, pricing, rules.
- `booking` — столы, брони, доступность, email-билеты, публичный билет.
- `catalog` — каталог настолок и продуктов (без заказов).
- `inbox` — форма контактов и сообщения клиентов.
- `staff` — кастомная панель персонала (CRUD, статусы броней, настройки).
- `site_settings` — singleton-настройки сайта + расписание (weekly/special days).
- `integrations` — Telegram-уведомления.

## 2) Ключевые модели
### `site_settings`
- `SiteSettings` — singleton с SEO/контактами/настройками бронирования/Telegram/Email.
  - Важно: `deposit_required` = `deposit_amount > 0`.
- `WeeklySchedule` — график по дням недели (0=Пн..6=Вс).
- `SpecialDay` — исключения по датам (перекрывают weekly).

### `booking`
- `Table` — столы (capacity, активность, примечание).
- `Reservation` — бронь с вычисляемым `end_time`, `public_code`, статусами.
  - Валидации: активность стола, seats <= capacity, доступность по расписанию,
    пересечения по времени, минимальное время уведомления.

### `catalog`
- `BoardGame` — настольные игры.
- `Product` — продукты/напитки.

### `inbox`
- `ContactMessage` — сообщения из формы контактов.

## 3) Ключевая бизнес-логика
### Доступность бронирования
Файл: `booking/services.py`
- `is_table_available(...)` — проверка пересечения слотов.
- `find_available_tables(...)` — доступные столы по времени/местам.
- `find_available_start_times_for_table(...)` — доступные слоты по столу.
- `find_available_tables_for_date(...)` — доступные столы в течение дня.

### Расписание
Файл: `booking/utils.py`
- `get_working_window(date)` — сначала `SpecialDay`, затем `WeeklySchedule`.
- `compute_end_time(...)` — вычисление окончания слота.

### Уведомления
- Email: `booking/notifications.py` — отправка билета.
- Telegram: `integrations/telegram.py` — отправка сообщения при включенной интеграции.

## 4) Публичные маршруты
Файл: `anti_cafe_reservation/urls.py`
- `/` → `landing`
- `/booking/` → `booking`
- `/games/`, `/products/` → `catalog`
- `/contact/` → `inbox`
- `/staff/` → `staff`
- `/admin/` → Django admin

Файлы маршрутов:
- `landing/urls.py`
- `booking/urls.py`
- `catalog/urls.py`
- `inbox/urls.py`
- `staff/urls.py`

## 5) Шаблоны и статика
- База: `templates/base.html`, `templates/staff/base_staff.html`
- Landing: `templates/landing/*.html`
- Booking: `templates/booking/*.html`
- Catalog: `templates/catalog/*.html`
- Inbox: `templates/inbox/contact.html`
- Staff UI: `templates/staff/*.html`
- Статика: `static/css/site.css`, `static/js/theme.js`, `static/images/logo.png`

## 6) Админка и панель персонала
### Админка
Модели подключены в `booking/admin.py`, `catalog/admin.py`, `inbox/admin.py`,
`site_settings/admin.py`.

### Панель персонала (`staff`)
- Дашборд с бронями на сегодня.
- Фильтр бронирований по дате/статусу.
- CRUD столов, игр, продуктов.
- Просмотр сообщений.
- Настройки сайта + графики работы.

## 7) Служебные команды
- `python manage.py seed_demo` — наполняет демо-данными.
  - Поддерживает флаги `--reset`, `--big`, `--with-special-days`, `--days`, `--realistic`.
- `python manage.py clear_all_data --yes` — очищает все данные приложения.

## 8) Настройки проекта
Файл: `anti_cafe_reservation/settings.py`
- БД: PostgreSQL по умолчанию, SQLite для тестов (если `DJANGO_TEST_USE_SQLITE=1`).
- Язык: `ru`, таймзона: `Europe/Moscow`.
- Email: по умолчанию `console` backend.

## 9) Тесты
Папка: `booking/tests/`
- Проверки правил бронирования, форм, доступности и view.
