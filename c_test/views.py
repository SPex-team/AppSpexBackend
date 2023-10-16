import time

from . import models as l_models
from . import serializers as l_serializers
from rest_framework import viewsets
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from spex import tasks as spex_tasks
from loan import tasks as loan_tasks


class TestUser(viewsets.ModelViewSet):
    queryset = l_models.User.objects.all()
    serializer_class = l_serializers.TestUser

    permission_classes = []

    def list(self, request, *args, **kwargs):
        html_message = "<h1>HHHHHHH</h1>"

        # send_mail("AAA", "mmm", from_email=settings.EMAIL_HOST_USER, recipient_list=["mingmingtang@aliyun.com"],
        #           html_message=html_message)

        if settings.ENV == "LOCAL":
            loan_tasks.update_all_loans()

        time.sleep(72)
        return Response({})

    def create(self, request, *args, **kwargs):
        html_message = "<h1>HHHHHHH</h1>"
        # send_mail("AAA", "mmm", from_email=settings.EMAIL_HOST_USER, recipient_list=["mingmingtang@aliyun.com"],
        #           html_message=html_message)
        # spex_tasks.update_all_miners()

        if settings.ENV == "LOCAL":
            loan_tasks.sync_new_miners()
        return Response({})
