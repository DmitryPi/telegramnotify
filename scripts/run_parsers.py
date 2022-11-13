import environ

from telegramservice.core.parsers import FLParser


def run():
    env = environ.Env()
    env.read_env(".env")
    fl_parser = FLParser(env)
    fl_parser.run()
