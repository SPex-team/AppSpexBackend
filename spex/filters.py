from django.db.models import Q

from django_filters import rest_framework as filters

from . import models as l_models


class Order(filters.FilterSet):
    seller_or_buyer = filters.CharFilter(method='c_seller_or_buyer')

    class Meta:
        model = l_models.Order
        fields = ["seller", "miner_id", "buyer", "transaction_hash", "seller_or_buyer"]
        # fields = {
        #     "seller": ["exact"],
        #     "is_list": ["exact"],
        #     "buyer": ["exact"],
        #     "seller_or_buyer": ["exact"]
        # }

    def c_seller_or_buyer(self, queryset, name, value):
        return queryset.filter(Q(seller=value) | Q(buyer=value))
