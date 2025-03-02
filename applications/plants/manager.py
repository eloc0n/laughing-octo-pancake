from django.db.models import (
    Avg,
    DecimalField,
    ExpressionWrapper,
    F,
    Manager,
    QuerySet,
    Sum,
)


class PlantQuerySet(QuerySet):
    def filter_active(self):
        return self.filter(is_archived=False)


class PlantManager(Manager.from_queryset(PlantQuerySet)):
    pass


class PlantDataPointQuerySet(QuerySet):
    def filter_active(self):
        return self.filter(plant__is_archived=False)

    def for_datapoint_retrieval(self):
        return self.values(
            "id",
            "energy_expected",
            "energy_observed",
            "irradiation_expected",
            "irradiation_observed",
            "datetime",
        )

    def for_datapoint_list(self, plant_id: str):
        return self.filter(plant_id=plant_id).values(
            "id",
            "energy_expected",
            "energy_observed",
            "irradiation_expected",
            "irradiation_observed",
            "datetime",
            "plant_id",
            plant_name=F("plant__name"),
        )

    def annotate_metrics(self):
        return self.values(plant_name=F("plant__name")).annotate(
            energy_expected_sum=Sum("energy_expected"),
            energy_observed_sum=Sum("energy_observed"),
            energy_expected_avg=Avg("energy_expected"),
            energy_observed_avg=Avg("energy_observed"),
            energy_efficiency=ExpressionWrapper(
                F("energy_observed_sum") / F("energy_expected_sum"),
                output_field=DecimalField(max_digits=15, decimal_places=10),
            ),
            irradiation_expected_sum=Sum("irradiation_expected"),
            irradiation_observed_sum=Sum("irradiation_observed"),
            irradiation_expected_avg=Avg("irradiation_expected"),
            irradiation_observed_avg=Avg("irradiation_observed"),
            irradiation_efficiency=ExpressionWrapper(
                F("irradiation_observed_sum") / F("irradiation_expected_sum"),
                output_field=DecimalField(max_digits=15, decimal_places=10),
            ),
        )


class PlantDataPointManager(Manager.from_queryset(PlantDataPointQuerySet)):
    pass
