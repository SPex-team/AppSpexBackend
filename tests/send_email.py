from django.core.mail import send_mail

import os
import sys
import django

from django.conf import settings

APP_NAME = "AppSpexBackend"

settings.configure(
    EMAIL_USE_TLS=True,
    EMAIL_HOST='smtp-mail.outlook.com',
    EMAIL_HOST_USER='hellman_alert@outlook.com',
    EMAIL_HOST_PASSWORD='wonders,1',
    EMAIL_PORT=25
)
django.setup()

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(BASE_DIR)
#
# APP_NAME = "AppSpexBackend"
#
# settings = f"{APP_NAME}.settings"
# os.environ["DJANGO_SETTINGS_MODULE"] = settings
#
# django.setup()


if __name__ == '__main__':
    r = send_mail(
        subject="Hellman Alert",
        message="performance is low 1",
        from_email="hellman_alert@outlook.com",
        recipient_list=["mingmingtang@aliyundnnsewm.com"]
    )
    print(r)
