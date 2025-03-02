from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from applications.plants.factories.plant import PlantFactory
from applications.plants.models import Plant


class PlantTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.plants = PlantFactory.create_batch(size=5)
        cls.archived_plant = PlantFactory(
            name="Archived Plant", is_archived=True
        )

    def test_plant_creation(self):
        url = reverse("plants-list")
        data = {"name": "Solar Plant 1"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Plant.objects.filter(id=response.data["id"]).count(), 1
        )

    def test_plant_creation_with_duplicate_name(self):
        url = reverse("plants-list")
        data = {
            "name": self.plants[0].name,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_plant(self):
        url = reverse("plants-detail", kwargs={"pk": str(self.plants[0].id)})
        data = {"name": "Best name for a solar plant!"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_archive_plant(self):
        url = reverse("plants-detail", kwargs={"pk": str(self.plants[0].id)})
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_cannot_find_archived_plant(self):
        url = reverse(
            "plants-detail", kwargs={"pk": str(self.archived_plant.id)}
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_plant(self):
        url = reverse("plants-detail", kwargs={"pk": str(self.plants[0].id)})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_plants(self):
        url = reverse("plants-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_filter_by_name(self):
        url = reverse("plants-list")
        response = self.client.get(
            url, {"search": self.plants[0].name}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_cannot_search_filter_by_name_of_archived_plant(self):
        url = reverse("plants-list")
        response = self.client.get(
            url, {"search": self.archived_plant.name}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_ordering_by_name(self):
        url = reverse("plants-list")
        response = self.client.get(url, {"ordering": "name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        names = [u["name"] for u in results]
        self.assertEqual(names, sorted(names))
