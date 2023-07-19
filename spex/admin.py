from django.contrib import admin


from . import models as l_models
from devops_django import models as dd_models


@admin.register(l_models.Miner)
class Miner(admin.ModelAdmin):
    list_display = dd_models.get_all_field_name(l_models.Miner)
    list_display_links = ("miner_id",)
    list_per_page = 10


@admin.register(l_models.Order)
class Order(admin.ModelAdmin):
    list_display = dd_models.get_all_field_name(l_models.Order)
    list_display_links = ("transaction_hash", )
    list_per_page = 10


@admin.register(l_models.Comment)
class Comment(admin.ModelAdmin):
    list_display = dd_models.get_all_field_name(l_models.Comment)
    list_display_links = ("id",)
    list_per_page = 10


@admin.register(l_models.Tag)
class Tag(admin.ModelAdmin):
    list_display = dd_models.get_all_field_name(l_models.Tag)
    list_display_links = ("key",)
    list_per_page = 10
