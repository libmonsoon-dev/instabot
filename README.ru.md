# INSTABOT
Скрипт для выполнения однотипных действий

## Установка
```bash
    pip install -r requirements.txt
```
## Использование
Скрипт конфигурируеться через переменные окружения или из файла .env на том же уровне, где и main.py, она же и точка входа.
Запуск:
```bash
    cd src
    python3 main.py
```
## Переменные окружения
### Основные параметры

INSTABOT_MODE - На данный момент единственное доступное значение (установлено по умолчаню) 'unfollow'

INSTABOT_REQUESTS_LIMIT - количество запросов до завершения цикла (по умолчанию - 1000)

INSTABOT_REQUESTS_INTERVAL - интервал между запросами в секундах (по умолчанию - 30)

INSTABOT_AJAX_HEADER

INSTABOT_RANDOM_INTERVALS

### Параметры пользователя

INSTABOT_USER_NAME - Логин

INSTABOT_USER_PASS - Пароль

INSTABOT_USER_QUERY_HASH - Необходимая для запросов строка. [Способ получения](https://github.com/mineur/instagram-parser/blob/master/docs/setup.md#how-to-get-your-query-hash-old-query-id)

### Параметры логирования

INSTABOT_LOGGING_FORMAT - Формат логирования (по умолчанию - '[%(asctime)s]\t%(levelname)s\t%(filename)s:%(lineno)d\t%(message)s'), [Подробнее](https://docs.python.org/3/library/logging.html#logging.Formatter)

INSTABOT_LOGGING_LEVEL - Уровень логирования. (по умалчанию - 'INFO' ) Доступные значения:
- 'CRITICAL'
- 'ERROR'
- 'WARNING'
- 'INFO'
- 'DEBUG'
- 'NOTSET'