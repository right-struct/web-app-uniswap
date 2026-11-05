# 🔄 UniSwap SDU — Платформа студенческого обмена

**UniSwap SDU** — это веб-платформа, созданная для студентов университета SDU (Сулейман Демирель), позволяющая удобно и быстро обмениваться учебными материалами, книгами, конспектами, гаджетами и вещами внутри университетского кампуса.

Проект построен на **Python/Django** с удалённой базой данных **PostgreSQL** в облаке Neon и адаптивным веб-интерфейсом.

---

## 🏗 Архитектура и структура проекта

Проект использует архитектуру **MVT (Model-View-Template)** с встроенным HTTP REST API для обмена данными между клиентом и сервером:

```text
uni-swap/
├── manage.py                  # Главная консольная утилита управления Django
├── requirements.txt           # Список необходимых библиотек и зависимостей
├── .gitignore                 # Исключение мусорных и временных файлов из Git
├── README.md                  # Данная документация
│
├── uni_swap/                  # Глобальная конфигурация проекта
│   ├── settings.py            # Настройки: подключение к Neon PostgreSQL, статика, приложения
│   ├── urls.py                # Главный URL-маршрутизатор
│   └── wsgi.py / asgi.py      # Точки входа для веб-серверов
│
├── main/                      # Основное приложение платформы
│   ├── models.py              # Модель данных Item (вещь для обмена)
│   ├── views.py               # Контроллеры страниц и REST API (GET, POST)
│   ├── urls.py                # Маршруты страниц (/search/, /account/) и API (/api/items/)
│   ├── admin.py               # Регистрация модели в панели администратора Django
│   ├── migrations/            # История миграций базы данных
│   └── static/main/           # Статические ресурсы (CSS, JS, изображения)
│       ├── css/main.css       # Стили интерфейса (цветовая палитра, тени, адаптив)
│       ├── img/               # Логотипы и фоновые изображения
│       └── js/                # Скрипты клиентской логики
│
└── templates/main/            # HTML-шаблоны
    ├── layout.html            # Базовый каркас (наследование через Jinja/DTL)
    ├── index.html             # Главная страница (Hero, навигация, логотип)
    └── search.html            # Интерактивная страница поиска и публикации вещей
```

---

## ⚡ Пошаговая инструкция по запуску с нуля

### 1. Предварительные требования
Убедитесь, что на компьютере установлен **Python 3.10** или новее:
```bash
python3 --version
```

### 2. Клонирование и переход в папку проекта
```bash
cd uni-swap
```
*(Убедитесь, что вы находитесь в папке, где лежит файл `manage.py`)*

### 3. Создание и активация виртуального окружения
* **Linux / macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
* **Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
*(После активации в начале строки терминала появится `(.venv)`)*

### 4. Установка зависимостей
```bash
pip install -r requirements.txt
```
В проект включены:
* `Django` — веб-фреймворк
* `dj-database-url` — парсер строки подключения БД
* `psycopg[binary]` — современный и быстрый драйвер PostgreSQL

### 5. Применение миграций базы данных
База данных уже настроена на облачный PostgreSQL (Neon):
```bash
python manage.py migrate
```

### 6. Запуск сервера разработки
```bash
python manage.py runserver
```

Теперь откройте в браузере:  
👉 **Главная страница:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)  
👉 **Поиск и добавление вещей:** [http://127.0.0.1:8000/search/](http://127.0.0.1:8000/search/)  
👉 **Панель администратора:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 📡 Документация HTTP REST API

Проект предоставляет готовый REST API для взаимодействия клиента (браузера, мобильного приложения или сторонних сервисов) с сервером.

### Эндпоинты

| Метод | URL | Описание | Формат тела |
|---|---|---|---|
| **GET** | `/api/items/` | Получить список всех активных вещей для обмена | Query-параметры: `?search=...`, `?category=...` |
| **POST** | `/api/items/` | Опубликовать новую вещь для обмена | JSON |
| **GET** | `/api/items/<id>/` | Получить подробную информацию о конкретной вещи | — |
| **DELETE**| `/api/items/<id>/` | Отметить вещь как обменянную / недоступную | — |

---

### Примеры запросов к API

#### 1. Получить список вещей (GET)
* **cURL:**
  ```bash
  curl http://127.0.0.1:8000/api/items/
  ```
* **JavaScript (fetch в браузере):**
  ```javascript
  const response = await fetch('/api/items/?search=Calculus');
  const data = await response.json();
  console.log(data.items);
  ```
* **Пример ответа (200 OK):**
  ```json
  {
    "success": true,
    "count": 1,
    "items": [
      {
        "id": 1,
        "title": "Calculus 8th Edition by Stewart",
        "description": "Good condition, want to swap for Discrete Math",
        "category": "books",
        "category_display": "Books & Notes",
        "contact": "@sdu_alex",
        "is_available": true,
        "created_at": "2026-11-05 09:32:36"
      }
    ]
  }
  ```

#### 2. Добавить новую вещь (POST)
* **cURL:**
  ```bash
  curl -X POST http://127.0.0.1:8000/api/items/ \
    -H "Content-Type: application/json" \
    -d '{
      "title": "Scientific Calculator Casio fx-991",
      "category": "electronics",
      "contact": "@sdu_student",
      "description": "Perfect for physics and exam sessions."
    }'
  ```
* **JavaScript (fetch):**
  ```javascript
  const res = await fetch('/api/items/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title: 'SDU Hoodie Size M',
      category: 'clothing',
      contact: 'student@sdu.edu.kz',
      description: 'Navy blue hoodie, swap for size L'
    })
  });
  const result = await res.json();
  ```
* **Пример ответа (201 Created):**
  ```json
  {
    "success": true,
    "item": {
      "id": 2,
      "title": "Scientific Calculator Casio fx-991",
      "category": "electronics",
      "category_display": "Electronics & Gadgets",
      "contact": "@sdu_student",
      "description": "Perfect for physics and exam sessions.",
      "is_available": true,
      "created_at": "2026-11-05 09:35:10"
    }
  }
  ```

---

## 🛠 Руководство по решению проблем (Troubleshooting)

### 1. «Error: That port is already in use» (Порт 8000 занят)
* **Причина:** Другой процесс (предыдущий запуск Django или другая программа) уже слушает порт `8000`.
* **Решение 1:** Запустите Django на другом свободном порту (например, `8080` или `8001`):
  ```bash
  python manage.py runserver 8080
  ```
* **Решение 2 (Linux):** Найти и завершить процесс:
  ```bash
  fuser -k 8000/tcp
  ```

### 2. Ошибки подключения к базе данных Neon (PostgreSQL connection timeout / drops)
* **Причина:** Облачный сервис Neon переводит неактивные базы данных в спящий режим для экономии ресурсов. Первый запрос после простоя может занять 2–4 секунды («холодный старт»).
* **Решение:**
  * Убедитесь, что у вас есть стабильное интернет-соединение.
  * Параметр `sslmode=require` обязателен (он уже включён в настройку `settings.py`).
  * Если нужно локально переопределить строку подключения, создайте системную переменную `DATABASE_URL`:
    ```bash
    export DATABASE_URL="postgresql://user:pass@host/dbname?sslmode=require"
    ```

### 3. Ошибка «./.venv/bin/python: Нет такого файла или каталога»
* **Причина:** Папка `.venv` была скопирована с другого компьютера. Внутри `.venv` пути к Python захардкожены абсолютными путями создателя.
* **Решение:** Удалите старую папку и пересоздайте её:
  ```bash
  rm -rf .venv
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

### 4. Картинки или стили не обновляются в браузере
* **Причина:** Браузер закэшировал старую версию CSS или картинок.
* **Решение:** Нажмите `Ctrl + F5` (или `Cmd + Shift + R` на Mac) для полной перезагрузки страницы со сбросом кэша.

### 5. Создание суперпользователя для панели администратора
Чтобы заходить в админку ([http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)) и управлять вещами вручную:
```bash
python manage.py createsuperuser
```
Введите имя, email и пароль.

---

Разработано для студентов SDU 🎓
