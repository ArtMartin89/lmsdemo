# Быстрое решение проблемы медленной сборки

## Вариант 1: Использовать китайское зеркало npm (если медленный интернет)

Отредактируйте `frontend/Dockerfile`, добавьте перед `npm install`:

```dockerfile
RUN npm config set registry https://registry.npmmirror.com/
```

## Вариант 2: Собрать локально и скопировать

1. В папке `frontend` выполните:
```bash
npm install
npm run build
```

2. Измените `frontend/Dockerfile` на:
```dockerfile
FROM nginx:alpine
COPY dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Вариант 3: Использовать готовый образ

Временно используйте готовый образ для разработки:
```yaml
frontend:
  image: nginx:alpine
  # ... остальное
```

## Вариант 4: Проверить интернет-соединение

Проверьте скорость загрузки npm пакетов:
```bash
docker run --rm node:18-alpine sh -c "time npm install react@18.2.0"
```

Если это занимает больше 30 секунд - проблема в интернете.


