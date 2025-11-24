# LMS Platform

Обучающая система с базой знаний и тестированием на основе FastAPI и React.

## Технологический стек

- **Backend:** Python (FastAPI), PostgreSQL, Redis
- **Frontend:** React + TypeScript, Vite, TailwindCSS
- **Deployment:** Docker + Docker Compose

## Структура проекта

```
.
├── backend/          # FastAPI приложение
├── frontend/         # React приложение
├── storage/          # Локальное хранилище контента (уроки, тесты)
├── docker-compose.yml
└── README.md
```

## Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Git

### Установка и запуск

1. Клонируйте репозиторий (если нужно)

2. Запустите приложение:
```bash
docker-compose up -d
```

3. Приложение будет доступно:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

4. Создайте тестового пользователя:
```bash
# Зарегистрируйтесь через API или используйте тестовые данные
# Username: testdemo
# Password: demotest
```

### Подготовка контента

Создайте структуру для уроков и тестов:

```bash
mkdir -p storage/lessons/Module_01
mkdir -p storage/tests/Module_01
```

Пример урока (`storage/lessons/Module_01/lesson_01.md`):
```markdown
# Урок 1: Введение

Это первый урок модуля.
```

Пример теста (`storage/tests/Module_01/test_questions.json`):
```json
{
  "module_id": "Module_01",
  "passing_threshold": 0.7,
  "time_limit_minutes": 30,
  "questions": [
    {
      "question_id": "q1",
      "type": "single_choice",
      "question": "Что такое Python?",
      "options": [
        {"id": "A", "text": "Язык программирования"},
        {"id": "B", "text": "База данных"},
        {"id": "C", "text": "Операционная система"}
      ],
      "points": 1
    }
  ]
}
```

Пример правильных ответов (`storage/tests/Module_01/correct_answers.json`):
```json
{
  "module_id": "Module_01",
  "answers": [
    {
      "question_id": "q1",
      "correct_answer": "A",
      "explanation": "Python - это язык программирования"
    }
  ]
}
```

### Инициализация базы данных

Модули нужно добавить в базу данных. Вы можете использовать SQL или создать скрипт миграции:

```sql
INSERT INTO modules (id, title, description, total_lessons, order_index) 
VALUES ('Module_01', 'Введение в Python', 'Основы языка программирования Python', 3, 1);
```

## Разработка

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Аутентификация
- `POST /api/v1/auth/register` - Регистрация
- `POST /api/v1/auth/login` - Вход
- `GET /api/v1/auth/me` - Текущий пользователь

### Модули
- `GET /api/v1/modules` - Список модулей
- `GET /api/v1/modules/{module_id}` - Детали модуля
- `POST /api/v1/modules/{module_id}/start` - Начать модуль

### Уроки
- `POST /api/v1/modules/{module_id}/next` - Следующий урок

### Тесты
- `GET /api/v1/modules/{module_id}/test` - Получить вопросы
- `POST /api/v1/modules/{module_id}/test` - Отправить ответы

### Прогресс
- `GET /api/v1/progress` - Общий прогресс
- `GET /api/v1/progress/{module_id}` - Прогресс по модулю

## Тестовые пользователи

По умолчанию доступны:
- **Обычный пользователь:**
  - Username: `testdemo`
  - Password: `demotest`
  
- **Администратор:**
  - Username: `admin`
  - Password: `admin`

Или зарегистрируйте нового пользователя через API.

## Остановка

```bash
docker-compose down
```

Для удаления данных:
```bash
docker-compose down -v
```

## Лицензия

MIT

