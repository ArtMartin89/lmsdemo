# Инструкция по запуску

## Запуск приложения

1. **Запустите все сервисы:**
```bash
docker-compose up -d
```

2. **Проверьте статус:**
```bash
docker-compose ps
```

3. **Проверьте логи frontend:**
```bash
docker-compose logs frontend
```

4. **Инициализируйте базу данных (после первого запуска):**
```bash
docker-compose exec api python init_db.py
```

## Доступ к приложению

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Тестовые пользователи

- **Обычный пользователь:**
  - Username: `testdemo`
  - Password: `demotest`

- **Администратор:**
  - Username: `admin`
  - Password: `admin`

## Если frontend не работает

1. Проверьте, что контейнер запущен:
```bash
docker-compose ps frontend
```

2. Проверьте логи:
```bash
docker-compose logs frontend
```

3. Пересоберите frontend:
```bash
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

4. Проверьте, что файлы собрались:
```bash
docker-compose exec frontend ls -la /usr/share/nginx/html
```

