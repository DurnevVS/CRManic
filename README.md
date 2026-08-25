# CRManic

CRM-система для мастеров маникюра.

## Требования

- Python 3.14 или новее;
- [uv](https://docs.astral.sh/uv/).

## Запуск на Linux

```bash
uv sync --dev
uv run python manage.py migrate
uv run python manage.py runserver
```

## Запуск на Windows

Выполните команды в PowerShell:

```powershell
uv sync --dev
uv run python manage.py migrate
uv run python manage.py runserver
```

После запуска проект доступен по адресу `http://127.0.0.1:8000/`, панель
администратора — `http://127.0.0.1:8000/admin/`.

API доступно по адресу `http://127.0.0.1:8000/api/v1/`, документация Swagger —
`http://127.0.0.1:8000/api/docs/`, схема OpenAPI —
`http://127.0.0.1:8000/api/schema/`.

Для создания администратора выполните:

```text
uv run python manage.py createsuperuser
```

## Авторизация API

Получите токен по номеру телефона и паролю мастера:

```bash
curl --request POST http://127.0.0.1:8000/api/v1/auth/token/ \
  --header "Content-Type: application/json" \
  --data '{"phone":"+79991234567","password":"password"}'
```

Передавайте полученный токен в защищённых запросах:

```text
Authorization: Token <token>
```

Основные ресурсы API:

- `/api/v1/clients/`;
- `/api/v1/services/`;
- `/api/v1/completed-services/`;
- `/api/v1/schedule-days/`;
- `/api/v1/appointment-slots/`;
- `/api/v1/expense-groups/`;
- `/api/v1/expenses/`;
- `/api/v1/expense-templates/`.

## Проверки

```bash
uv run python manage.py test
uv run python manage.py spectacular --validate --fail-on-warn
uv run pyrefly check
```
