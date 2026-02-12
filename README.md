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

### 2) Создать базу данных и пользователя PostgreSQL (подробно, для начинающих)
По умолчанию проект ожидает следующие параметры (см. `anti_cafe_reservation/settings.py`):
- DB: `anti_cafe_reservation`
- USER: `anti_cafe`
- PASSWORD: `anti_cafe`
- HOST: `localhost`
- PORT: `5432`

#### 2.1 Войти в psql под суперпользователем
Если PostgreSQL установлен локально, обычно доступен пользователь `postgres`.
```powershell
psql -U postgres
```

Если вход выполнен, вы увидите приглашение вида `postgres=#`.

#### 2.2 Создать пользователя (роль)
```sql
CREATE USER anti_cafe WITH PASSWORD 'anti_cafe';
```

#### 2.3 Создать базу данных и назначить владельца
```sql
CREATE DATABASE anti_cafe_reservation OWNER anti_cafe;
```

#### 2.4 Выдать привилегии пользователю (рекомендуется)
```sql
GRANT ALL PRIVILEGES ON DATABASE anti_cafe_reservation TO anti_cafe;
```

Подключиться к созданной БД и выдать права на схему `public`:
```sql
\c anti_cafe_reservation
GRANT ALL ON SCHEMA public TO anti_cafe;
```

Если планируется, что пользователь будет создавать таблицы (миграции), можно
назначить права по умолчанию:
```sql
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO anti_cafe;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO anti_cafe;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO anti_cafe;
```

Выйти из psql:
```sql
\q
```

Если вы хотите использовать другие параметры подключения, измените их в
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
