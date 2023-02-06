from django.contrib import admin


from . import models as l_models
from devops_django import models as dd_models


@admin.register(l_models.Miner)
class MinerAdmin(admin.ModelAdmin):
    list_display = dd_models.get_all_field_name(l_models.Miner)
    exclude = ("miner_id", )
    list_display_links = ("miner_id",)
    list_per_page = 10
