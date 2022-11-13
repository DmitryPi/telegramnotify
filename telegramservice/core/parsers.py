from environ import Env

from telegramservice.core.models import Target


class FLParser:
    def __init__(self, env: Env):
        self.env = env
        self.target = ""
        self.set_target()

    def set_target(self):
        try:
            target = Target.objects.get(title="FL.ru")
            self.target = target.url_body
        except Target.DoesNotExist as e:
            print("Target you are trying to find DoesNotExist")
            raise e

    def run(self):
        print(self.target)
