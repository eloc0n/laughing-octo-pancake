from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from applications.plants.factories.plant import DataPointFactory, PlantFactory


class PlantDataPointTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.plants = PlantFactory.create_batch(size=5)
        for plant in cls.plants:
            DataPointFactory.create_batch(5, plant=plant)
        cls.archived_plant = PlantFactory(
            name="Archived Plant", is_archived=True
        )
        DataPointFactory.create_batch(5, plant=cls.archived_plant)

    def test_cannot_find_archived_plant(self):
        url = reverse(
            "datapoints-detail",
            kwargs={
                "plant_id": str(self.archived_plant.id),
                "pk": str(self.archived_plant.datapoints.first().id),
            },
        )
        with self.assertNumQueries(1):
            response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_specific_datapoint_of_plant(self):
        url = reverse(
            "datapoints-detail",
            kwargs={
                "plant_id": str(self.plants[0].id),
                "pk": str(self.plants[0].datapoints.first().id),
            },
        )
        with self.assertNumQueries(1):
            response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_plant_datapoints(self):
        url = reverse(
            "datapoints-list",
            kwargs={
                "plant_id": str(self.plants[0].id),
            },
        )
        with self.assertNumQueries(2):
            response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_uuid(self):
        url = reverse(
            "datapoints-list",
            kwargs={
                "plant_id": "invalid-id",
            },
        )
        with self.assertNumQueries(0):
            response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
