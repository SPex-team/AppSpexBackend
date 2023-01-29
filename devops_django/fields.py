import json

from django.contrib.postgres import fields as p_fields
from django.db import models


class JSONField(models.Field):

    def db_type(self, connection):
        assert connection.settings_dict['ENGINE'] == 'django.db.backends.mysql', "The storeage of JSON field must be Mysql"
        return "JSON"

    def from_db_value(self, value, expression, connection):
        return json.loads(value)

    def get_prep_value(self, value):
        json_str = json.dumps(value)
        return json_str
