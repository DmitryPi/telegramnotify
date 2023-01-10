# [TelegramNotify](https://telegramnotify.ru/)

> Телеграм сервис оповещений о новых заказах и проектах по ключевым словам
> Реализован на языке Python, путем слияния django и telegram-bot-api
> Функцинал: регистрации пользователя, пополнение кошелька, настройка оповещений, обратная связь

Версия: 1.0.0

## TODO

- TelegramBot - тестирование нескольких функций, у которых имеется TODO в описании
- TelegramBot - доработка кнопок команды /settings
- Заглушка на основном домене, ведущая на тг бот
- Очистка файлов от всего лишнего и не нужного

### Type checks

Running type checks with mypy:

    $ mypy telegramnotify

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest

## Deployment

The following details how to deploy this application.


## Версии

1.0.0 release
- Регистрация пользователя
- Личный кабинет пользователя в телеграм
- Доступно обновление настроек пользователем
- Подписки на сервис: Expired, Trial, Regular, Permanent
- Реализованные сервисы подписки: FL.ru
- Возможность обратной связи по средству телеграм и админки джанго
