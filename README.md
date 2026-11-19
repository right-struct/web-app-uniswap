# UniSwap SDU

Платформа студенческого обмена SDU на Django. Проект использует Django Templates, PostgreSQL (по `DATABASE_URL`) и приложение `main` для объявлений и профилей пользователей.

> **Тестовые данные для разработки.** Эти общедоступные учётные данные нельзя использовать в production. После разработки удалите тестовые аккаунты или замените их пароли.

| Username | Email | Password | Role |
|---|---|---|---|
| test_user | test.user@sdu.edu.kz | TestUser_2026! | regularUser |
| test_moderator | test.moderator@sdu.edu.kz | TestMod_2026! | moderator |
| test_admin | test.admin@sdu.edu.kz | TestAdmin_2026! | admin |

Проверено в основной PostgreSQL `neondb`: все записи активны, пароли проходят `check_password()`, роли соответствуют таблице. `test_admin` не является Django superuser и не имеет `is_staff`.

## Возможности и ограничения реализации

- Публичной регистрации нет. Вход только по email и паролю, выход через Django auth views, сессии и CSRF.
- Пароли хешируются Django. Rate limit ограничивает попытки по email/IP; используется локальный cache по умолчанию, Redis можно включить через `REDIS_CACHE_URL`.
- Email для обычных пользователей должен иметь домен `sdu.edu.kz` или `stu.sdu.edu.kz` при создании через управляемую форму. База гарантирует непустой email и уникальность без учёта регистра.
- Роли лежат в `main_userprofile`. Назначение выполняет сервер/администратор. `regularUser` управляет своими объявлениями; moderator/admin могут также удалять чужие. `admin` в UniSwap не означает `is_staff`/доступ к Django Admin.
- Объявления публично читаются. API поддерживает создание (сессия требуется), обновление владельцем и soft-delete владельцем или moderator/admin. Интерфейс главной страницы получает реальные карточки из API; полноценные формы создания/редактирования и отдельная HTML-страница деталей пока не реализованы.
- Wishlist, публичное управление избранным, пагинация, полная модераторская панель сайта и уведомления не реализованы.

## Модели и база

PostgreSQL подключается из `.env` через `DATABASE_URL`; секреты в README не хранятся. При отсутствии переменной настройки переключаются на локальную `db.sqlite3`, но основная база проекта — PostgreSQL.

| Таблица | Назначение |
|---|---|
| `auth_user` | Стандартная Django User: username, email, password hash, активность и Django permissions flags. Email ограничен уникальным индексом на `LOWER(email)` и проверкой непустого значения. |
| `main_userprofile` | Связь OneToOne с `auth_user`, роль `regularUser` / `moderator` / `admin`, даты создания и изменения профиля. |
| `main_item` | Объявление: title, description, category, contact, listing_type, price, image, owner, is_available, created_at, updated_at. `owner_id` — nullable FK к `auth_user`, старые объявления без владельца допустимы. |
| `django_session` | Серверные сессии Django. |
| `auth_group`, `auth_permission`, `auth_user_groups`, `auth_user_user_permissions` | Стандартные группы и разрешения Django. |
| `django_content_type`, `django_admin_log`, `django_migrations` | Служебные таблицы Django. |

Категории — фиксированные choices: `books`, `electronics`, `clothing`, `services`, `other`. Типы — choices `Sale`, `Swap`, `Looking`, `Free`. Отдельные таблицы не нужны, пока справочники фиксированы; оба значения хранятся в строковых полях `main_item.category` и `main_item.listing_type`.

Фотография одна на объявление, поле `image` — ImageField до 5 MiB, формат проверяется сервером. Файлы сохраняются в `MEDIA_ROOT` (по умолчанию каталог `media/`) и выдаются по `MEDIA_URL=/media/`. Для production раздачу медиа следует настроить на веб-сервере или объектном хранилище.

Миграции `main`: `0001_initial`, `0002_item_updated_at_alter_item_category`, `0003_item_owner_userprofile`, `0004_user_email_constraints`, `0005_item_image_item_listing_type_item_price`.

## API

Ответы JSON. `GET` публичен; изменяющие методы требуют Django session и CSRF-токен. Для JSON POST/PUT/PATCH передавайте `X-CSRFToken`.

| Метод | URL | Назначение / доступ |
|---|---|---|
| GET | `/api/items/` | Список доступных объявлений; параметры `search`, `category`, `type`. |
| POST | `/api/items/` | Создать объявление; авторизация обязательна. Поля: `title`, `description`, `category`, `contact`, `type`, `price`, опционально файл `image` (multipart). |
| GET | `/api/items/<id>/` | Детали объявления, публично. |
| PUT, PATCH | `/api/items/<id>/` | Обновить объявление владельцу; JSON-поля `title`, `description`, `contact`, `category`, `type`, `price`. |
| DELETE | `/api/items/<id>/` | Пометить объявление недоступным; владелец или moderator/admin. Это soft-delete, строка сохраняется. |

Формат списка: `{success, count, items}`; одиночное объявление: `{success, item}`. Ошибки возвращают `{success: false, error}` и HTTP-статус. Объявления с `owner=NULL` нельзя редактировать обычному пользователю; moderator/admin может сделать их недоступными.

## Страницы и URL

`/`, `/search/`, `/account/`, `/wishlist/`, `/legal/`, `/help/`, `/mail/`; вход `/auth/login/`, выход `/auth/logout/`; Django Admin `/admin/`.

## Запуск

1. Клонируйте репозиторий и перейдите в каталог проекта.
2. Создайте окружение и установите зависимости:

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Создайте `.env` рядом с `manage.py`, не добавляя его в Git:

```dotenv
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
# необязательно для общей защиты при нескольких workers:
# REDIS_CACHE_URL=redis://localhost:6379/1
```

4. Создайте PostgreSQL базу и задайте корректные секреты в `.env`. Не публикуйте строку подключения или `DJANGO_SECRET_KEY`.
5. Примените миграции и создайте администратора Django:

```bash
python manage.py migrate
python manage.py createsuperuser
```

6. При необходимости создать отсутствующие тестовые аккаунты запустите `python manage.py ensure_test_accounts`. Команда запросит пароли интерактивно и не перезаписывает существующие учётные данные.
7. Запустите сервер: `python manage.py runserver`.
8. Сайт: http://127.0.0.1:8000/ ; Django Admin: http://127.0.0.1:8000/admin/ .

Тесты с отдельной SQLite базой запускаются командой:

```bash
DJANGO_TEST_SQLITE=1 python manage.py test
```

## Структура проекта

```text
manage.py
requirements.txt
.env                         # локальные секреты, не коммитить
uni_swap/                    # settings.py, urls.py, ASGI/WSGI
main/                        # модели, views, forms, auth backend, admin, tests
main/migrations/             # история схемы
main/management/commands/    # ensure_test_accounts
main/static/main/             # CSS, JavaScript, изображения интерфейса
templates/main/               # Django HTML-шаблоны
media/                        # пользовательские изображения (создаётся при загрузке)
```

Зависимости включают Django 5.2, `dj-database-url`, `psycopg`, `python-dotenv` и Pillow.
