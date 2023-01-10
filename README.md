# TelegramService

> Телеграм сервис оповещений о новых заказах и проектах по ключевым словам
> Осуществлен на языке Python, путем слияния django и telegram-bot-api
> Доступна функция регистрации пользователя, пополнение кошелька, кастомизация оповещений

> Версия: 1.0.0


## TODO

- TelegramBot - тестирование нескольких функций, у которых имеется 'TODO' в __doc__
- TelegramBot - проработка кнопок команды /settings
- Переименовать проект TelegramService и root folder => ?


### Type checks

Running type checks with mypy:

    $ mypy telegramservice

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
- Возможность обратной связи по средству телеграм и джанго
