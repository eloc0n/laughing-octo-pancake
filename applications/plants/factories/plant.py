import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import factory

from applications.plants.models import DataPoint, Plant


class PlantFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating plant instances.
    """

    name = factory.Faker("name")
    is_archived = False

    class Meta:
        model = Plant


class DataPointFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating data point instances.
    """

    plant = factory.SubFactory(PlantFactory)
    datetime = factory.LazyFunction(
        lambda: (
            datetime.now(timezone.utc)
            - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
            )
        ).replace(minute=0, second=0, microsecond=0)
    )
    energy_expected = factory.LazyFunction(
        lambda: Decimal(f"{random.uniform(5.0, 10.0):.10f}")
    )
    irradiation_expected = factory.LazyFunction(
        lambda: Decimal(f"{random.uniform(40.0, 60.0):.10f}")
    )
    energy_observed = factory.LazyFunction(
        lambda: Decimal(f"{random.uniform(70.0, 90.0):.10f}")
    )
    irradiation_observed = factory.LazyFunction(
        lambda: Decimal(f"{random.uniform(70.0, 100.0):.10f}")
    )

    class Meta:
        model = DataPoint
