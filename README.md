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

Для создания администратора выполните:

```text
uv run python manage.py createsuperuser
```
