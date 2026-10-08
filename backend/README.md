# Backend «Близкие» — лабораторная №2

FastAPI отвечает за HTTP API, Pydantic — за схемы запросов и ответов, SQLAlchemy — за операции с PostgreSQL. Маршруты вызывают операции в `app/services`; соединения и сессии находятся в `app/db`, настройки и обработчики ошибок — в `app/core`. Миграции Alembic создают таблицы явно: запуск приложения не меняет схему БД и не загружает демо автоматически.

## Установка

Проверено с Python 3.13.3 и PostgreSQL 18.4. Команды ниже выполняются в PowerShell **из папки `backend`**. Команда `python --version` должна показывать Python 3.13. Активация виртуального окружения не обязательна.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Для запуска без тестов и Ruff достаточно `requirements.txt`.

## PostgreSQL и окружение

Выберите один из двух вариантов настройки.

### Отдельный локальный кластер проекта на Windows

При установленном PostgreSQL 18:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start-local-postgres.ps1
```

Скрипт использует утилиты из `C:\Program Files\PostgreSQL\18\bin`. Если установка находится в другом месте:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start-local-postgres.ps1 -PostgresBin 'C:\Program Files\PostgreSQL\17\bin'
```

Скрипт создаёт кластер в `.local/postgres`, слушающий `127.0.0.1:55432`, две базы `family_health` и `family_health_test`, а также `.env` с автоматически сгенерированным паролем. Повторный запуск поднимает тот же кластер и сохраняет данные. Системная служба PostgreSQL работает независимо. При существующем вручную заполненном `.env` скрипт откажется его перезаписывать; используйте ручной вариант ниже.

Для остановки именно этого кластера:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/stop-local-postgres.ps1
```

Если использовали `-PostgresBin`, передайте его и команде остановки. Порт можно изменить через `-Port`; при последующих запусках передавайте тот же порт. Скрипт создаёт роль администратора только своего локального учебного кластера.

### Существующий PostgreSQL

Выполните под администратором PostgreSQL, например через SQL-консоль pgAdmin:

```sql
CREATE ROLE family_health LOGIN PASSWORD 'replace_with_your_local_password';
CREATE DATABASE family_health OWNER family_health;
CREATE DATABASE family_health_test OWNER family_health;
```

Каждый `CREATE DATABASE` выполняется отдельно, вне транзакции. Затем:

```powershell
Copy-Item .env.example .env
```

В `.env` замените `CHANGE_ME` собственным паролем и при необходимости адрес, порт и имя базы. Пример содержит только заглушки:

```dotenv
DATABASE_URL=postgresql+psycopg://family_health:CHANGE_ME@127.0.0.1:5432/family_health
TEST_DATABASE_URL=postgresql+psycopg://family_health:CHANGE_ME@127.0.0.1:5432/family_health_test
APP_NAME=Blizkie API
CORS_ORIGINS=["http://127.0.0.1:5173","http://localhost:5173"]
```

Специальные символы пароля в URL нужно кодировать как percent-encoding. Настройки читаются из `backend/.env` независимо от текущего каталога; переменные процесса имеют приоритет. Допускается драйвер `postgresql+psycopg`. Настройка SQLite отклоняется.

`.env`, `.local`, `.venv`, кэш и результаты тестов исключены из Git. В репозиторий добавляется только `.env.example` без действующих секретов.

## Таблицы, демо и сервер

После настройки БД:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m scripts.seed
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --reload --host 127.0.0.1 --port 8000
```

`seed` необязателен. Он добавляет одну вымышленную семью, трёх человек, пять назначений и шесть отметок на **07.10.2026**, две из которых приняты. Если демо-семья уже существует, повторный запуск ничего не меняет. Примеры предназначены для демонстрации проекта.

После запуска доступны:

- Swagger UI: http://127.0.0.1:8000/docs — формы запросов и точные схемы.
- OpenAPI: http://127.0.0.1:8000/openapi.json.
- Проверка сервера и подключения к БД: http://127.0.0.1:8000/health.

`Ctrl+C` останавливает Uvicorn. Отдельный кластер БД останавливается своей командой выше. Данные сохраняются после перезапуска сервера и PostgreSQL.

## Модель данных

```mermaid
erDiagram
    families ||--o{ family_members : contains
    family_members ||--o{ medications : has
    medications ||--|{ medication_times : scheduled_at
    medications ||--o{ intakes : recorded_as
```

Все основные сущности имеют UUID PK. `family_members.family_id`, `medications.member_id`, `medication_times.medication_id` и `intakes.medication_id` — внешние ключи с `ON DELETE CASCADE`. У времени приёма составной PK `(medication_id, time)`; повторное время в одном назначении запрещено. Поля связей в PATCH не меняются: назначение создаётся для конкретного человека, отметка — для конкретного назначения.

Назначение содержит название препарата, форму, дозу, инструкцию, даты курса и от одного до двенадцати ежедневных времён. Начало и конец включаются в курс; `end_date=null` означает бессрочный курс. Дата рождения хранится вместо возраста, поэтому возраст вычисляется при чтении. Семья служит группировкой данных; аккаунты и проверки прав появятся в ЛР №4.

Время расписания — местное время без часового пояса с точностью до минуты. Дата расписания передаётся явно в `day`; расписание не привязано к фиксированной демо-дате. `taken_at` — момент отметки с часовым поясом, формируется сервером. PostgreSQL хранит его как `timestamp with time zone`; смещение в ответе зависит от настройки часового пояса соединения. Повторное `taken=true` сохраняет исходный момент отметки, `taken=false` очищает его. Нельзя отмечать будущий календарный день как принятый; сегодняшний день определяется часами сервера.

Расписание строится из действующих назначений и объединяется с сохранёнными отметками за выбранный день. Для ещё не записанного приёма возвращаются `intake_id=null`, `taken=false`; GET не создаёт записи в базе. Изменение курса или времени, противоречащее существующим отметкам, отклоняется с `409`, чтобы сохранить согласованность истории.

## HTTP API

Базовый префикс — `/api/v1`. Для каждого из ресурсов `families`, `members`, `medications`, `intakes`:

| Метод и путь | Результат |
| --- | --- |
| `POST /{resource}` | Создание, `201`, объект и заголовок `Location` |
| `GET /{resource}` | Список, `200`; `offset ≥ 0`, `1 ≤ limit ≤ 200`, по умолчанию 100 |
| `GET /{resource}/{id}` | Один объект, `200` |
| `PATCH /{resource}/{id}` | Частичное изменение, `200`; требуется хотя бы одно поле |
| `DELETE /{resource}/{id}` | Удаление, `204` без тела |

Фильтры списков:

- `members`: `family_id`.
- `medications`: `family_id`, `member_id`.
- `intakes`: `family_id`, `member_id`, `medication_id`, `day`.

Дополнительные запросы:

| Запрос | Назначение |
| --- | --- |
| `GET /schedule?family_id={uuid}&day=YYYY-MM-DD` | Расписание семьи; необязательные `member_id`, `taken=true/false` |
| `GET /members/{id}/doctor-list?day=YYYY-MM-DD` | Данные человека, активные назначения, число плановых и принятых приёмов |

`doctor-list` возвращает JSON для будущей интеграции с печатным экраном. Доставка напоминаний, авторизация и подключение React к API относятся к следующим этапам. Вторая лабораторная проверяется через Swagger UI или HTTP-запросы.

### Пример полного сценария в PowerShell

В отдельном терминале при работающем сервере:

```powershell
$api = 'http://127.0.0.1:8000/api/v1'
function Send-Json($method, $path, $body) {
    $jsonBytes = [System.Text.Encoding]::UTF8.GetBytes(($body | ConvertTo-Json -Depth 5))
    Invoke-RestMethod -Method $method -Uri ($api + $path) -ContentType 'application/json; charset=utf-8' -Body $jsonBytes
}
$family = Send-Json POST '/families' @{ name = 'Моя семья' }
$member = Send-Json POST '/members' @{
    family_id = $family.id; full_name = 'Анна Петрова'; birth_date = '2000-05-14'; relation = 'Я'
}
$medication = Send-Json POST '/medications' @{
    member_id = $member.id; name = 'Учебный препарат'; form = 'Таблетки'; dose = '1 таблетка'
    instructions = 'После еды'; start_date = '2020-01-01'; times = @('08:00', '20:00')
}
$intake = Send-Json POST '/intakes' @{
    medication_id = $medication.id; scheduled_date = '2020-01-02'; scheduled_time = '08:00'; taken = $false
}
Send-Json PATCH ('/intakes/' + $intake.id) @{ taken = $true }
Invoke-RestMethod "$api/schedule?family_id=$($family.id)&day=2020-01-02"
Invoke-RestMethod "$api/members/$($member.id)/doctor-list?day=2020-01-02"
# Удаляет только созданную в этом примере семью и её связанные записи:
Invoke-RestMethod -Method DELETE -Uri "$api/families/$($family.id)"
```

Пример демо-расписания:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/api/v1/schedule?family_id=57894a99-7ce7-532f-8345-11c9fd1cfa20&day=2026-10-07'
```

### Ошибки и ограничения

| Статус | Пример |
| --- | --- |
| `404` | Объект или родитель для создаваемой записи не найден |
| `409` | Повторная отметка того же назначения/даты/времени; изменение расписания нарушает историю |
| `422` | Неверный UUID, дата, пустое поле, неизвестное поле, неверное время, несовместимые фильтры |
| `503` | Ошибка доступа к БД; ответ не раскрывает адрес и пароль |

Обязательные поля PATCH не принимают `null`; `end_date` можно явно очистить. Строки обрезаются по краям и проверяются по длине. Дата рождения — от 01.01.1900 до сегодня. Время приёма не должно повторяться, содержать секунды или часовой пояс. Дата отметки должна входить в курс, время — в расписание назначения. БД независимо обеспечивает PK, FK, уникальность отметки, порядок дат курса и согласованность `taken`/`taken_at`.

В ответе об ошибке используется `detail`: строка для предметной ошибки либо список с `loc`, `type`, `msg` для ошибки схемы. Неверные данные запроса не отражаются целиком в ответе.

## Проверки

Для тестов требуется `TEST_DATABASE_URL` в переменных процесса или `.env`. Имя базы обязано заканчиваться на `_test`, а роль должна иметь возможность создавать схемы в ней. Нет подмены PostgreSQL на SQLite и пропуска тестов при отсутствии базы.

Каждый тест создаёт схему `lab2_test_<случайный UUID>`, применяет настоящую миграцию и направляет в неё соединения. В конце удаляется только созданная этим тестом схема. При принудительном завершении процесса схема может остаться в тестовой базе; рабочая база не используется тестами.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m alembic check
.\.venv\Scripts\python.exe -m ruff check app migrations scripts tests
.\.venv\Scripts\python.exe -m ruff format --check app migrations scripts tests
.\.venv\Scripts\python.exe -m pip check
```

Проверяются CRUD четырёх сущностей, чтение через новую сессию и заново созданное приложение, каскадное удаление, реальные ограничения PostgreSQL, валидация, конфликты и восстановление после них, расписание и список врача, идемпотентность демо, CORS, недоступность БД, соответствие и обратимость миграции. Результаты проверки этапа сохранены в [docs/lab2-verification.md](../docs/lab2-verification.md).
