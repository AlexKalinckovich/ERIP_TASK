## Настройка окружения

Перед запуском необходимо создать файл `.env.test` в корневой директории.
Пример, как должен выглядть .env.test описан в .env.example и продублирован ниже с конкретными
значениями( Шарю, что в проде .env не надо ни в каком виде пушить, но Вам так будет легче :) )
```env
ENVIRONMENT=test
LOG_LEVEL=DEBUG

POSTGRES_USER=test_user
POSTGRES_PASSWORD=test_password
POSTGRES_DB=currency_test_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

DATABASE_URL=postgresql+asyncpg://test_user:test_password@db:5432/currency_test_db

NBRB_API_BASE_URL=https://api.nbrb.by
NBRB_TIMEOUT=5.0
NBRB_MAX_RETRIES=3
NBRB_RETRY_BACKOFF=0.5
NBRB_RETRY_JITTER=0.1

LIQUIBASE_SEARCH_PATH=/liquibase/changelog
LIQUIBASE_COMMAND_URL=jdbc:postgresql://db:5432/currency_test_db
LIQUIBASE_COMMAND_USERNAME=test_user
LIQUIBASE_COMMAND_PASSWORD=test_password

APP_PORT=8000
```

## Запуск приложения

Запустите все сервисы:

```bash
docker compose up -d
```

## Доступ к приложению

После запуска сервисы будут доступны по следующим адресам:

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/swagger-ui`
- Dozzle (логи): `http://localhost:9999`
- PostgreSQL: `localhost:5432`

## Структура сервисов

- **app** - FastAPI приложение
- **db** - PostgreSQL база данных
- **liquibase** - миграции базы данных 
- **dozzle** - веб-интерфейс для просмотра логов контейнеров
- **sonarqube** - quality gate
