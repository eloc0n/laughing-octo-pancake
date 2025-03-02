from django.contrib import admin

from .models import DataPoint, Plant


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    readonly_fields = ["id"]
    list_display = (
        "id",
        "name",
    )


@admin.register(DataPoint)
class DataPointAdmin(admin.ModelAdmin):
    readonly_fields = ["id"]
    list_display = (
        "id",
        "plant",
        "datetime",
        "energy_expected",
        "energy_observed",
        "irradiation_expected",
        "irradiation_observed",
    )

    search_fields = ["plant__name"]
