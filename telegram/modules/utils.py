import codecs
import configparser
from datetime import datetime, timedelta


def build_config(config_name="config.ini") -> None:
    """Build default config section key/values"""
    config = configparser.ConfigParser()
    config.update(
        {
            "MAIN": {
                "debug": True,
            },
            "TELEGRAM": {
                "api_token": "",
                "admin_id": "",
                "admin_password": 1234,
            },
            "SENTRY": {"dsn": "", "log_level": 20},
        }
    )
    with open(config_name, "w") as f:
        print("- Creating new config")
        config.write(f)


def load_config(config_fp="config.ini"):
    """load config from `config_fp`; build default if not found"""
    config = configparser.ConfigParser()
    try:
        config.read_file(codecs.open(config_fp, "r", "utf8"))
    except FileNotFoundError:
        print("- Config not found")
        build_config()
        config.read_file(codecs.open(config_fp, "r", "utf8"))
    return config


def handle_error(error, to_file=False, to_file_path="error_log.txt"):
    """Handle error by writing to file/sending to sentry/raising"""
    if to_file:
        with open(to_file_path, "a", encoding="utf-8") as f:
            f.write(error + "\n")
    else:
        raise error


def datetime_days_ahead(days: int) -> datetime:
    now = datetime.now()
    delta = timedelta(days=days)
    return now + delta
