import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from applications.plants.manager import PlantDataPointManager, PlantManager


class Plant(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    # NOTE: I am making the assumption that
    # 'plant-id' from monitoring service is
    # a unique identifier and mapping it with field name.
    name = models.CharField(
        max_length=256, blank=False, null=False, editable=True, unique=True
    )
    is_archived = models.BooleanField(default=False)

    objects = PlantManager()

    class Meta:
        verbose_name = _("Plant")
        verbose_name_plural = _("Plants")

    def __str__(self):
        return self.name

    def archive(self):
        """
        Archives the Plant entry instead of deleting it.
        """
        self.is_archived = True
        self.save()


class DataPoint(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    plant = models.ForeignKey(
        "Plant",
        on_delete=models.CASCADE,
        related_name="datapoints",
        blank=False,
        null=False,
    )
    energy_expected = models.DecimalField(
        max_digits=15, decimal_places=10, blank=False, null=False
    )
    energy_observed = models.DecimalField(
        max_digits=15, decimal_places=10, blank=False, null=False
    )
    irradiation_expected = models.DecimalField(
        max_digits=15, decimal_places=10, blank=False, null=False
    )
    irradiation_observed = models.DecimalField(
        max_digits=15, decimal_places=10, blank=False, null=False
    )
    datetime = models.DateTimeField(blank=False, null=False)

    objects = PlantDataPointManager()

    class Meta:
        verbose_name = _("Data Point")
        verbose_name_plural = _("Data Points")

    def __str__(self):
        return f"Data point of plant {self.plant.name}"
