# Food Plan
Командный проект на Django.

## ⚙️ Технический стек
- **База данных**: SQLite / PostgreSQL в Docker _(опционально)_
- **Бэкенд**: Python 3.x, Django 6.x
- **Фронтенд**: Django Templates

## 📂 Структура проекта
```text
.
├── apps/               # Папка для Django-приложений
│   ├── menu/           # Рецепты, ингредиенты и аллергены 
│   ├── pages/          # Страницы общего назначения
│   └── users/          # Аунтентификация пользователей и личный кабинет
├── food_plan/          # Настройки проекта (settings, urls, wsgi)
├── static/             # Глобальные статические файлы (css, assets)
├── templates/          # Глобальные HTML шаблоны
├── docker-compose-dev.yaml
├── manage.py
└── requirements.txt
```

## 🛠️ Установка и Настройка
#### 1. Клонируйте репозиторий:
```bash
git clone https://github.com/VictoriaL-dev/food-plan.git
cd food-plan
```

#### 2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
venv\Scripts\activate # на Windows
source venv/bin/activate # на Linux / macOS
```

#### 3. Установите зависимости:
```bash
pip install -r requirements.txt
```

#### 4. Настройте переменные окружения. На основе `.env.example` создайте `.env` файл:
```dotenv
# Django
SECRET_KEY="your_django_secret_key"
DEBUG=True
ALLOWED_HOSTS="127.0.0.1,localhost"

# PostgreSQL
POSTGRES_USER=db_user
POSTGRES_PASSWORD=db_password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5433
POSTGRES_DB=db_name
DATABASE_URL="postgresql://db_user:db_password@127.0.0.1:5432/db_name"

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER="example@email.com"
EMAIL_HOST_PASSWORD="abcdefghijklmnop" # 16-значный пароль приложения
DEFAULT_FROM_EMAIL="example@email.com"
```

#### 5. Запустите базу данных через Docker Compose _(опционально)_:
```bash
docker-compose -f docker-compose-dev.yaml up -d
```

#### 6. Примените миграции и создайте суперпользователя:
```bash
python manage.py migrate
python manage.py createsuperuser
```

#### 7. Запустите сервер:
```bash
python manage.py runserver
```

## 🚀 Использование (рекомендованный Workflow)
#### 1. Актуальность: всегда начинайте работу с подтягивания свежих изменений из основной ветки:
```bash
git checkout main
git pull origin main
```
#### 2. Разработка: создавайте отдельную ветку под каждую задачу:
```bash
git checkout -b feat/<имя-задачи>
```

#### 3. Коммит, мердж и пуш:
```bash
git add .
git commit -m "type(scope): что сделано" # feat(db): add model...
git checkout main
git merge feat/<имя-задачи>
git push origin main
```

#### 4. Завершение: после вашего Pull Request (merge), удаляйте локальную ветку:
```bash
git checkout main
git pull origin main
git branch -d feat/<имя-задачи>
```
