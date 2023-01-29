
import datetime
import threading

from django.conf import settings
from django.apps import AppConfig
from django.db import models
from django.db import models as django_models


def get_all_field_name(model):
    fields = [i.name for i in model._meta.fields]
    # fields.reverse()
    return fields


class IdToDateFormatMixin:

    """
    id 必须为BigInt
    """

    _lock = threading.Lock()
    _end_length = 6

    def save(self, *args, **kwargs):
        if self.id:
            super().save(*args, **kwargs)
            return
        self._lock.acquire()
        try:
            today_string = datetime.datetime.now().strftime("%y%m%d")
            id_range = (int(today_string + "0" * self._end_length), int(today_string + "9" * self._end_length))
            try:
                last_instance = self.__class__.objects.filter(id__range=id_range).order_by("-id")[0]
            except IndexError:
                index = 1
            else:
                id_date_string = str(last_instance.id)[:6]
                if today_string == id_date_string:
                    index = int(str(last_instance.id)[6:]) + 1
                else:
                    index = 1
            index_string = f"%0{self._end_length}d" % index
            id = int(today_string + index_string)
        finally:
            self._lock.release()
        self.id = id
        return super().save(*args, **kwargs)


def get_table_model_map():
    _map = {}
    for entry in settings.INSTALLED_APPS:
        if isinstance(entry, AppConfig):
            app_config = entry
        else:
            app_config = AppConfig.create(entry)
        if not hasattr(app_config.module, "models"):
            continue
        models_module = getattr(app_config.module, "models")
        for item in dir(models_module):
            attribute = getattr(models_module, item)
            if not isinstance(attribute, django_models.base.ModelBase):
                continue
            _map[attribute._meta.db_table] = attribute
    return _map


class Lock(models.Model):
    key = models.CharField(primary_key=True, max_length=100)
    timestamp = models.FloatField()

    create_time = models.DateTimeField(db_index=True, auto_now=True)
    update_time = models.DateTimeField(auto_now_add=True)
