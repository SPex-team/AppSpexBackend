
from django_filters import rest_framework as filters

from . import models as l_models


class Miner(filters.FilterSet):

    class Meta:
        model = l_models.Miner
        fields = {
            "owner": ["exact"],
            "is_list": ["exact"],
        }
