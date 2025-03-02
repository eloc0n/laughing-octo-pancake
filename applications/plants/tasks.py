from datetime import datetime, timedelta, timezone
from typing import List, Optional

import requests
from celery import shared_task
from django.conf import settings
from django.utils.dateparse import parse_datetime

from applications.plants.models import DataPoint, Plant
from applications.plants.serializers import MonitoringServiceSerializer

MONITORING_API_URL_TEMPLATE = (
    settings.INTERNAL_MONITORING_API_URL
    + "?plant-id={plant_id}&from={from_date}&to={to_date}"
)


"""
Task to pull data from monitoring service
every day at 1am.

Things to consider.
- Should i consider that the plant exists in my database ?
  If it does not should i create a plant and ingest datapoints ?
- What happens in case the service is down? Do we retry and when
  or just wait for the next periodic execution.
- If am i to retry, i should only retry for the failed calls
  Meaning that i have to store failed calls somewhere (maybe in Redis).
- The response data seems like it is not paginated
  But then again we need to fetch past 24 hours data
  and the service returns hourly data. So max number of
  data per plant is 24.
- Handling in case of missing data
- Include logger / alert
- Maybe an email report with failed updated / created actions
"""


def execute_fetching_in_background(plant_names: List):
    result = fetch_monitoring_data.apply_async(
        kwargs={"plant_names": plant_names},
        eta=datetime.now(timezone.utc) + timedelta(seconds=1),
    )
    return result.id


def make_request(url: str):
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    return response.json()


def bulk_update_or_create(
    datetime_plant_mapping: dict, existing_mapping: dict, plant: Plant
):
    new_data_points = []
    updated_data_points = []

    for timestamp, entry in datetime_plant_mapping.items():
        existing = existing_mapping.get(timestamp)

        expected = entry.get("expected", {})
        observed = entry.get("observed", {})

        if existing:
            # NOTE: Existing data might be the same so we probably
            # should skip the update action (currently not handled)

            # Update existing data point
            existing.energy_expected = expected.get("energy")
            existing.energy_observed = observed.get("energy")
            existing.irradiation_expected = expected.get("irradiation")
            existing.irradiation_observed = observed.get("irradiation")
            updated_data_points.append(existing)
        else:
            # Create new data point
            new_data_points.append(
                DataPoint(
                    plant=plant,
                    datetime=timestamp,
                    energy_expected=expected.get("energy"),
                    energy_observed=observed.get("energy"),
                    irradiation_expected=expected.get("irradiation"),
                    irradiation_observed=observed.get("irradiation"),
                )
            )

    if new_data_points:
        DataPoint.objects.bulk_create(new_data_points)

    if updated_data_points:
        DataPoint.objects.bulk_update(
            updated_data_points,
            [
                "energy_expected",
                "energy_observed",
                "irradiation_expected",
                "irradiation_observed",
            ],
        )


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_monitoring_data(self, plant_names: Optional[List[str]] = None):
    """
    Background task to fetch monitoring data from the
    monitoring service and store it.
    """
    try:
        if plant_names:
            plants = Plant.objects.filter_active().filter(name__in=plant_names)
        else:
            plants = Plant.objects.filter_active()
        if not plants:
            print("No active plants found!")
            return

        now = datetime.now(timezone.utc)
        from_date = now - timedelta(days=1)
        to_date = now

        from_date_str = from_date.strftime("%Y-%m-%d")
        to_date_str = to_date.strftime("%Y-%m-%d")

        # Fetch data for each plant
        for plant in plants:
            url = MONITORING_API_URL_TEMPLATE.format(
                plant_id=plant.name,
                from_date=from_date_str,
                to_date=to_date_str,
            )

            data = make_request(url)

            serializer = MonitoringServiceSerializer(data=data, many=True)
            if serializer.is_valid():
                datetime_plant_mapping = serializer.validated_data
            else:
                print("Invalid data:", serializer.errors)

            datetime_plant_mapping = {}
            for entry in data:
                datetime_str = entry.get("datetime")
                expected = entry.get("expected", {})
                observed = entry.get("observed", {})
                if datetime_str and expected and observed:
                    timestamp = parse_datetime(datetime_str)
                    datetime_plant_mapping[
                        timestamp.replace(tzinfo=timezone.utc)
                    ] = entry

            existing_data_points = DataPoint.objects.select_related(
                "plant"
            ).filter(datetime__in=datetime_plant_mapping.keys(), plant=plant)

            existing_mapping = {dp.datetime: dp for dp in existing_data_points}

            bulk_update_or_create(
                datetime_plant_mapping, existing_mapping, plant
            )

    except requests.exceptions.RequestException as e:
        raise self.retry(exc=e) from e
    except Exception as e:
        print(f"Error fetching data: {e}")
        raise Exception from e
