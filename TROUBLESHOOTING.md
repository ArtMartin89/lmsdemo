# Решение проблем с входом

## Проблема: Не могу войти с тестовыми данными

### Шаг 1: Проверьте, что контейнеры запущены

```bash
docker-compose ps
```

Все сервисы должны быть в статусе "Up".

### Шаг 2: Инициализируйте базу данных

```bash
docker-compose exec api python check_and_init.py
```

Или используйте старый скрипт:
```bash
docker-compose exec api python init_db.py
```

Вы должны увидеть сообщения:
- ✓ Test user created: testdemo / demotest
- ✓ Admin user created: admin / admin

### Шаг 3: Проверьте, что API работает

Откройте в браузере: http://localhost:8000/docs

Попробуйте выполнить запрос на `/api/v1/auth/login`:
```json
{
  "username": "admin",
  "password": "admin"
}
```

### Шаг 4: Проверьте логи API

```bash
docker-compose logs api --tail=50
```

Ищите ошибки подключения к базе данных.

### Шаг 5: Проверьте подключение к базе данных

```bash
docker-compose exec api python -c "from app.config import settings; print(settings.DATABASE_URL)"
```

### Шаг 6: Пересоздайте базу данных (если ничего не помогает)

```bash
docker-compose down -v
docker-compose up -d
docker-compose exec api python check_and_init.py
```

## Доступные тестовые пользователи

- **testdemo** / **demotest**
- **admin** / **admin**

## Проверка в браузере

Откройте консоль разработчика (F12) и проверьте:
1. Запросы к API (вкладка Network)
2. Ошибки в консоли (вкладка Console)
3. Правильный ли URL используется для API


