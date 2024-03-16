![GitHub](https://img.shields.io/github/license/LaGGgggg/yp_p2p_api?label=License)
![GitHub watchers](https://img.shields.io/github/watchers/LaGGgggg/yp_p2p_api?style=flat)
![GitHub last commit](https://img.shields.io/github/last-commit/LaGGgggg/yp_p2p_api)

# API для p2p оценки проектов студентов в Яндекс практикуме

# Как запустить проект?

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/LaGGgggg/yp_p2p_api.git
cd yp_p2p_api
```

### 2. Создайте виртуальное окружение

#### С помощью [pipenv](https://pipenv.pypa.io/en/latest/):

```bash
pip install --user pipenv
pipenv shell  # create and activate
```

#### Или классическим методом:

```bash
python -m venv .venv  # create
.venv\Scripts\activate.bat  # activate
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Установите переменные окружения (environment variables)

Создайте файл `.env`, это должно выглядеть так: `yp_p2p_api/API/core/.env`. После скопируйте это в `.env`

```dotenv
SECRET_KEY=<your_secret_key>
DATABASE_URL=postgresql://<username>:<password>@localhost:5432/<database_name>
ORIGINS="http://127.0.0.1:8000, http://localhost:8000"
ACCESS_TOKEN_EXPIRE_MINUTES=120
TOKEN_URL=token
ALGORITHM=HS256
DEBUG=True
DATABASE_URL_TEST=postgresql://<username>:<password>@localhost:5432/<database_name>  # не является обязательным
```
_**Не забудьте поменять значения на свои! (поставьте его после "=")**_

#### Больше о переменных:
SECRET_KEY - [секретный ключ](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/?h=secret#handle-jwt-tokens)
для хеширования паролей в базе данных<br>
DATABASE_URL - [url базы данных](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) sqlalchemy<br>
ORIGINS - [origins](https://fastapi.tiangolo.com/tutorial/cors/#origin) для
[CORSMiddleware](https://fastapi.tiangolo.com/tutorial/cors/#use-corsmiddleware)<br>
ACCESS_TOKEN_EXPIRE_MINUTES - значение по умолчанию для истечения токена авторизации
[LoginManager-а](https://fastapi-login.readthedocs.io/reference/#fastapi_login.fastapi_login.LoginManager)
(сколько пройдёт минут до того момета, как токен авторизации перестанет работать и нужно будет заново входить в систему)<br>
ALGORITHM - [алгоритм](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/?h=algorithm#hash-and-verify-the-passwords)
для хеширования паролей в базе данных<br>
DEBUG - True/False, определяет логику логирования, в продакшене должен (must) быть False<br>
DATABASE_URL_TEST - [url базы данных](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) sqlalchemy для тестирования.
До тех пор, пока вы не проводите запуск тестов с pytest, вам можно не устанавливать эту переменную окружения<br>

### 5. Перейдите в корневой каталог API

```bash
cd API
```

### 6. Запустите миграции базы данных

```bash
alembic upgrade head
```

### 7. Запустите проект

```bash
uvicorn core.main:app --reload
```

# Продакшен настройка

### 1. Установите [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

### 2. Установите [docker](https://docs.docker.com/engine/install/)

### 3. Установите [docker compose plugin](https://docs.docker.com/compose/install/linux/)

### 4. Клонируйте репозиторий

```bash
git clone https://github.com/LaGGgggg/yp_p2p_api.git
cd yp_p2p_api
```

### 5. Установите переменные окружения (environment variables)

Создайте файл `.env`, это должно выглядеть так: `yp_p2p_api/API/core/.env`. После скопируйте это в `.env`

```dotenv
SECRET_KEY=<your_secret_key>
DATABASE_URL=postgresql://<username>:<password>@localhost:5432/<database_name>
ORIGINS="http://127.0.0.1:8000, http://localhost:8000"
ACCESS_TOKEN_EXPIRE_MINUTES=120
TOKEN_URL=token
ALGORITHM=HS256
DEBUG=True

# docker-compose section
POSTGRES_USER=<username>
POSTGRES_PASSWORD=<password>
POSTGRES_DB=<database_name>
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
PGDATA=/var/lib/postgresql/data/pgdata
```
_**Не забудьте поменять значения на свои! (поставьте его после "=")**_

#### Больше о переменных:
SECRET_KEY - [секретный ключ](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/?h=secret#handle-jwt-tokens)
для хеширования паролей в базе данных<br>
DATABASE_URL - [url базы данных](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) sqlalchemy<br>
ORIGINS - [origins](https://fastapi.tiangolo.com/tutorial/cors/#origin) для
[CORSMiddleware](https://fastapi.tiangolo.com/tutorial/cors/#use-corsmiddleware)<br>
ACCESS_TOKEN_EXPIRE_MINUTES - значение по умолчанию для истечения токена авторизации
[LoginManager-а](https://fastapi-login.readthedocs.io/reference/#fastapi_login.fastapi_login.LoginManager)
(сколько пройдёт минут до того момета, как токен авторизации перестанет работать и нужно будет заново входить в систему)<br>
ALGORITHM - [алгоритм](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/?h=algorithm#hash-and-verify-the-passwords)
для хеширования паролей в базе данных<br>
DEBUG - True/False, определяет логику логирования, в продакшене должен (must) быть False<br>

POSTGRES_USER - [POSTGRES_USER](https://hub.docker.com/_/postgres) стандартная переменная окружения docker<br>
POSTGRES_PASSWORD - [POSTGRES_PASSWORD](https://hub.docker.com/_/postgres) стандартная переменная окружения docker<br>
POSTGRES_DB - [POSTGRES_DB](https://hub.docker.com/_/postgres) стандартная переменная окружения docker<br>
POSTGRES_HOST - [POSTGRES_HOST](https://hub.docker.com/_/postgres) стандартная переменная окружения docker<br>
POSTGRES_PORT - [POSTGRES_PORT](https://hub.docker.com/_/postgres) стандартная переменная окружения docker<br>
PGDATA - [PGDATA](https://hub.docker.com/_/postgres) стандартная переменная окружения docker<br>

### 6. Настройте [nginx.conf](nginx/nginx.conf)

Настройте доменное имя (вставьте его в кавычки, вместо domain.site):
```nginx configuration
set $domain_name "domain.site";
```

### 7. Настройте [docker-compose-init.sh](docker-compose-init.sh)

Настройте следующее (_3-5 строки в docker-compose-init.sh_):
```bash
domains=()  # example: (domain.site www.domain.site)
email=""  # example: "example@yandex.ru"
staging=0  # 1 - staging on, 0 - off
```

### 8. Запустите [docker-compose-init.sh](docker-compose-init.sh)

```bash
chmod +x docker-compose-init.sh
sudo ./docker-compose-init.sh
```

_*после первого успешного запуска таким способом для повтороного запуска можно использовать `docker compose up -d`_

### 9. После успешного запуска проверьте сервер

```bash
docker compose logs -f
```

# [utils.py](API/utils.py)

Это файл, который может исполнять команды:
```bash
# создаёт пользователя со всеми правами
# *вместо "username", "password" и "discord_id" подставьте свои имя пользователя, пароль и discord id
python utils.py create_superuser username password discord_id
```

# [pytest_runner.py](API/pytest_runner.py)

В проекте есть поддержка тестирования с [pytest](https://docs.pytest.org/en/stable/). Запускать pytest
рекомендуется при помощи [pytest_runner.py](API/pytest_runner.py). Этот файл сначала очистит тестовую базу данных,
потом применит все миграции alembic, и только после этого запустит pytest. Такие меры позволяют корректно работать
с базой данных в ходе тестирования.<br>
*Однако, вы всё ещё можете запустить pytest классическим способом, но помните, что
вам необходимо будет самостоятельно подготовить тестовую базу данных.*
```bash
python pytest_runner.py
```

# Об архитектуре

## [API/core](API/core):
Тут находятся core файлы, отвечающие за общие и основные вещи

### [config.py](API/core/config.py):
Создаются настройки API, брать их необходимо отсюда

### [get_logger.py](API/core/get_logger.py):
Общее место для получения логеров

### [login_manager.py](API/core/login_manager.py):
Место создания [LoginManager-а](https://fastapi-login.readthedocs.io/reference/#fastapi_login.fastapi_login.LoginManager),
получать его следует отсюда

### [schemas.py](API/core/schemas.py):
Место расположения [схем](https://fastapi.tiangolo.com/how-to/separate-openapi-schemas/?h=schemas) API

### [main.py](API/core/main.py):
Файл, инициализирующий и запускающий API, точка входа

## [API/migrations](API/migrations):
Внутри хранится логика миграций [alembic](https://alembic.sqlalchemy.org/en/latest/)

## [API/routers](API/routers)
Внутри хранятся [router-ы](https://fastapi.tiangolo.com/tutorial/bigger-applications/#apirouter) API

### [system.py](API/routers/system.py)
Логика переадресации ошибочных url и отображения автоматической документации API

### [users.py](API/routers/users.py)
Логика аутентификации и авторизации пользователей

## [API/sql](API/sql)
Логика базы данных

### [crud.py](API/sql/crud.py)
Логика взаимодействия с базой данных согласно [CRUD](https://ru.wikipedia.org/wiki/CRUD),
другие части API должны (must) использовать функции отсюда для взаимодействия с базой данных

### [database.py](API/sql/database.py)
Другие части API должны (must) получать сессию базы данных отсюда

### [models.py](API/sql/models.py)
Модели базы данных

# Для колобораторов

- Мы стараемся придерживаться [этого соглашения о коммитах](https://www.conventionalcommits.org/ru/v1.0.0/).
- Все коммиты и обсуждения мы проводим **по-русски**.
- В коде **всё**, кроме контента для пользователей (сообщения, которые бот отправляет пользователю и т.п.),
на **английском языке**.
- Коммиты первоначально осуществляются в **отдельную** ветку (специально созданную для этих коммитов из **dev** ветки), 
после отправляются в **dev** (посредством pull request-а), только потом в **main**.
