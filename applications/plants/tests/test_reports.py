from django.db.models import Q
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from applications.plants.factories.plant import DataPointFactory, PlantFactory
from applications.plants.models import DataPoint, Plant


class ReportsTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.plants = PlantFactory.create_batch(size=5)
        for plant in cls.plants:
            DataPointFactory.create_batch(5, plant=plant)
        cls.archived_plant = PlantFactory(
            name="Archived Plant", is_archived=True
        )
        DataPointFactory.create_batch(5, plant=cls.archived_plant)

    def test_display_stats_for_both_archived_and_active_plants(self):
        url = reverse("reports-list")
        response = self.client.get(
            url,
            {
                "show_archived": "true",
            },
            format="json",
        )
        plants = Plant.objects.filter(
            Q(is_archived=False) | Q(is_archived=True)
        ).count()
        self.assertEqual(plants, len(response.data["results"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_display_stats_for_active_plants(self):
        url = reverse("reports-list")
        response = self.client.get(
            url,
            {
                "show_archived": "false",
            },
            format="json",
        )
        plants = Plant.objects.filter(is_archived=False).count()
        self.assertEqual(plants, len(response.data["results"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_filter_by_name(self):
        url = reverse("reports-list")
        response = self.client.get(
            url, {"search": self.plants[0].name}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_ordering_by_name(self):
        url = reverse("reports-list")
        response = self.client.get(url, {"ordering": "name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        names = [u["plant_name"] for u in results]
        self.assertEqual(names, sorted(names))

    def test_filter_by_datetime(self):
        url = reverse("reports-list")
        qs = (
            DataPoint.objects.select_related("plant")
            .filter(plant__is_archived=False)
            .order_by("datetime")
        )
        rhs = qs.first().datetime
        lhs = qs.last().datetime
        response = self.client.get(
            url,
            {
                "show_archived": "false",
                "start_datetine": lhs,
                "end_datetine": rhs,
            },
            format="json",
        )
        count = (
            DataPoint.objects.select_related("plant")
            .filter(plant__is_archived=False, datetime__range=(rhs, lhs))
            .distinct("plant_id")
            .count()
        )
        self.assertEqual(response.data["count"], count)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
