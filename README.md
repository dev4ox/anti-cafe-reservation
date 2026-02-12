# Anti-cafe Reservation

Django-приложение для бронирования антикафе: сайт, бронирования, каталог, контакты, панель персонала.

## Быстрый обзор
- Главная: `/`
- Бронирование: `/booking/`
- Каталог игр: `/games/`
- Каталог продуктов: `/products/`
- Контакты: `/contact/`
- Панель персонала: `/staff/`
- Админка: `/admin/`

## Требования
- Python 3.11+ (рекомендуется 3.12)
- PostgreSQL 14+
- Windows PowerShell (или любой shell)

## Установка и запуск (полный цикл)

### 1) Создать виртуальное окружение и установить зависимости
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2) Создать базу данных и пользователя PostgreSQL
По умолчанию проект ожидает следующие параметры (см. `anti_cafe_reservation/settings.py`):
- DB: `anti_cafe_reservation`
- USER: `anti_cafe`
- PASSWORD: `anti_cafe`
- HOST: `localhost`
- PORT: `5432`

Создать пользователя и БД:
```powershell
psql -U postgres -c "CREATE USER anti_cafe WITH PASSWORD 'anti_cafe';"
psql -U postgres -c "CREATE DATABASE anti_cafe_reservation OWNER anti_cafe;"
```

Если вы хотите использовать другие параметры, измените их в
`anti_cafe_reservation/settings.py`.

### 3) Применить миграции
```powershell
python manage.py migrate
```

### 4) Создать суперпользователя
```powershell
python manage.py createsuperuser
```

### 5) Заполнить демо-данными
```powershell
python manage.py seed_demo --reset --with-special-days --days 7 --realistic --big
```

### 6) Запустить сервер
```powershell
python manage.py runserver
```

Откройте:
- http://127.0.0.1:8000/
- http://127.0.0.1:8000/staff/
- http://127.0.0.1:8000/admin/

## Очистка данных после демо
Чтобы удалить все данные приложений (брони, столы, каталог, сообщения, настройки, расписание):
```powershell
python manage.py clear_all_data --yes
```

Чтобы дополнительно удалить все загруженные файлы (MEDIA_ROOT):
```powershell
python manage.py clear_all_data --yes --with-media
```

Пользователи и учетные записи админки не удаляются.

## Примечания
- Email отправляется через `console` backend по умолчанию (см. `anti_cafe_reservation/settings.py`).
- Telegram-уведомления включаются в настройках сайта (`SiteSettings`).
