import os

ENV_CHOICES = ("LOCAL", "DEV", "FAT", "UAT", "PT", "PRO")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_NAME = BASE_DIR.rsplit("/", 1)[-1]
ENV = os.environ.get("ENV", "LOCAL")
if ENV not in ENV_CHOICES:
    raise Exception(f"非法环境变量ENV: {ENV}")


def get_django_settings():
    if ENV == "LOCAL":
        settings = "{}.settings".format(APP_NAME)
    else:
        if ENV not in ENV_CHOICES:
            raise Exception(f"环境变量ENV必须为{ENV_CHOICES}")
        settings = f"{APP_NAME}.settings_{ENV.lower()}"
    print(f"settings: {settings}")
    return settings
    # os.environ["DJANGO_SETTINGS_MODULE"] = settings
