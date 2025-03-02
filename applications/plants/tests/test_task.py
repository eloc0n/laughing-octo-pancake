from unittest.mock import patch

import requests
from django.test import TestCase
from django.utils import timezone

from applications.plants.factories.plant import DataPointFactory, PlantFactory
from applications.plants.models import DataPoint
from applications.plants.tasks import fetch_monitoring_data


class FetchMonitoringDataTestCase(TestCase):
    @patch("applications.plants.tasks.make_request")
    def test_fetch_monitoring_data_success(self, mock_get):
        """
        Test that fetch_monitoring_data fetches data correctly,
        creates new data points.
        """
        now = timezone.now().date()

        # Mock the response from the monitoring service
        mock_get.return_value.status_code = 200
        mock_get.return_value = [
            {
                "datetime": now.strftime("%Y-%m-%dT%H:%M:%S"),
                "expected": {
                    "energy": 14.4380684864,
                    "irradiation": 49.7343806849,
                },
                "observed": {
                    "energy": 15.6980684864,
                    "irradiation": 31.5543806849,
                },
            }
        ]

        plant = PlantFactory(name="my-plant-id")

        # Run the task synchronously
        fetch_monitoring_data()

        # Check if a DataPoint was created
        datapoint = DataPoint.objects.first()
        self.assertEqual(datapoint.plant, plant)
        self.assertEqual(float(datapoint.energy_expected), 14.4380684864)
        self.assertEqual(float(datapoint.energy_observed), 15.6980684864)
        self.assertEqual(float(datapoint.irradiation_expected), 49.7343806849)
        self.assertEqual(float(datapoint.irradiation_observed), 31.5543806849)

    @patch("applications.plants.tasks.make_request")
    def test_fetch_monitoring_data_retry_on_failure(self, mock_get):
        """
        Test that fetch_monitoring_data retries when the API request fails.
        """

        # Simulate a network error or failed request
        mock_get.side_effect = requests.exceptions.RequestException(
            "API request failed"
        )

        # Create a mock plant
        PlantFactory(name="my-plant-id")

        with self.assertRaises(requests.exceptions.RequestException):
            fetch_monitoring_data()

        mock_get.assert_called_once()
        # Check that no DataPoints are created
        self.assertEqual(DataPoint.objects.count(), 0)

    @patch("applications.plants.tasks.make_request")
    def test_fetch_monitoring_data_update_existing_datapoint(self, mock_get):
        """
        Test that fetch_monitoring_data correctly updates an existing data
        point.
        """
        # Create a mock plant and an existing data point
        plant = PlantFactory(name="my-plant-id")
        now = timezone.now()
        existing_datapoint = DataPointFactory(
            plant=plant,
            datetime=now.replace(hour=0, minute=0, second=0, microsecond=0),
        )

        dt = now.date().strftime("%Y-%m-%dT%H:%M:%S")
        self.assertEqual(
            existing_datapoint.datetime.strftime("%Y-%m-%dT%H:%M:%S"), dt
        )

        # Mock the response from the monitoring service
        mock_get.return_value.status_code = 200
        mock_get.return_value = [
            {
                "datetime": dt,
                "expected": {
                    "energy": 14.4380684864,
                    "irradiation": 49.7343806849,
                },
                "observed": {
                    "energy": 15.6980684864,
                    "irradiation": 31.5543806849,
                },
            }
        ]

        # Run the task synchronously
        fetch_monitoring_data()

        # Check if the existing DataPoint was updated
        existing_datapoint.refresh_from_db()
        self.assertEqual(
            float(existing_datapoint.energy_expected), 14.4380684864
        )
        self.assertEqual(
            float(existing_datapoint.energy_observed), 15.6980684864
        )
        self.assertEqual(
            float(existing_datapoint.irradiation_expected), 49.7343806849
        )
        self.assertEqual(
            float(existing_datapoint.irradiation_observed), 31.5543806849
        )
