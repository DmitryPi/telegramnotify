# [TelegramNotify](https://telegramnotify.ru/)

> Телеграм сервис оповещений о новых заказах и проектах по ключевым словам
> Реализован на языке Python, путем слияния django и telegram-bot-api
> Функцинал: регистрации пользователя, пополнение кошелька, настройка оповещений, обратная связь, парсеры, celery-задачи

Версия: 1.0.0

## TODO
---------------

- TelegramBot - тестирование нескольких функций, у которых имеется TODO в описании
- TelegramBot - доработка кнопок команды /settings
- Заглушка на основном домене, ведущая на тг бот
- Регистрация пользователя - шифрование пароля
- Очистка проекта от всего лишнего

## Testing
---------------
### Type checks

Running type checks with mypy:

    mypy telegramnotify

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    coverage run -m pytest
    coverage html
    open htmlcov/index.html

#### Running tests with pytest

    $ pytest

## Deployment
---------------
1. build the stack
    `docker-compose -f production.yml build`

2. migrate db
    `docker-compose -f production.yml run --rm django python manage.py migrate`

3. run containers
    `docker-compose -f production.yml up`
    run detached
    `docker-compose -f production.yml up -d`

4. create superuser
    `docker-compose -f production.yml run --rm django python manage.py createsuperuser`

### Optional commands
    # containers status
    docker-compose -f production.yml ps

    # containers logs
    docker-compose -f production.yml logs

    # django shell run
    docker-compose -f production.yml run --rm django python manage.py shell

    # If you want to scale application (❗ Don’t try to scale postgres, celerybeat, or traefik):
    docker-compose -f production.yml up --scale django=4
    docker-compose -f production.yml up --scale celeryworker=2



### Errors
1. ACME certificate failure: (unable to generate a certificate for the domains)


## Версии
---------------

1.0.0 release
- Регистрация пользователя
- Личный кабинет пользователя в телеграм
- Доступно обновление настроек пользователем
- Подписки на сервис: Expired, Trial, Regular, Permanent
- Реализованные сервисы подписки: FL.ru
- Возможность обратной связи по средству телеграм и админки джанго
- Контроль задач в celery
- Задачи на парсинг сервисов
- Задачи по обновление подписок
