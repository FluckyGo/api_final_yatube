# API_Final - законченная версия API для yatube.

#### Технологии

- Python
- Django 
- Django Rest Framework
- Djoser 
- Simple JWT
- SQLite3

### Как запустить проект:

Клонировать репозиторий:

```
git clone https://github.com/FluckyGo/api_final_yatube.git
```
Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Перейти в проект в командной строке:
```
cd yatube_api
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

Просмотр документации к API:

```
http://127.0.0.1:8000/redoc/
