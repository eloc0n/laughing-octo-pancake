import uuid

from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import GenericViewSet

from applications.plants.filters import ReportsFilterBackend
from applications.plants.mixins import SerializerActionClassMixin
from applications.plants.pagination import PageNumberPagination
from applications.plants.tasks import execute_fetching_in_background

from .models import DataPoint, Plant
from .serializers import (
    DataPointSerializer,
    PlantDataPointSerializer,
    PlantSerializer,
    ReportsSerializer,
)


class PlantViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    GenericViewSet,
):
    """
    Viewset for CRUD actions on Plants.
    """

    queryset = Plant.objects.filter_active()
    serializer_class = PlantSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    pagination_class = PageNumberPagination
    search_fields = ["name"]
    ordering_fields = ["name"]
    ordering = ["name"]

    def perform_destroy(self, instance):
        """
        Archive the Plant entry instead of deleting it.
        """
        instance.archive()

    @action(
        detail=True, methods=["POST"], url_name="ingest", url_path="ingest"
    )
    def ingest(self, request, *args, **kwargs):
        """
        Action for ingesting datapoints of a Plant

        Assuming that plant exists.
        Steps:
        - Retrieve plant_id (Could also include from and to)
        - Pass arguments into a function that submits
          a shared celery task and run in the background
        - Perform pulling of data and update or create

        For simplicity lets make the assumption that we
        are pulling data up to today, even though the
        monitoring service creates on the fly when asking
        for future dates.

        TODO:
        - A similar action (or adjust this) that could support bulk actions.
          Accept a list of plant_ids and perform celery task.
        - Include an action for checking celery task status.
        - Add flower for dev visibility.
        """
        plant = self.get_object()
        task_id = execute_fetching_in_background([plant.name])

        return Response(
            data={"task_id": task_id}, status=status.HTTP_202_ACCEPTED
        )


class PlantDataPointViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    SerializerActionClassMixin,
    GenericViewSet,
):
    """
    Viewset for list and retrieve actions on Plants datapoints.
    """

    queryset = DataPoint.objects.select_related("plant").filter_active()
    serializer_class = PlantDataPointSerializer
    pagination_class = PageNumberPagination
    serializer_action_classes = {"retrieve": DataPointSerializer}

    def get_queryset(self):
        if self.action == "list":
            if plant_id := self.kwargs.get("plant_id"):
                try:
                    uuid.UUID(plant_id)
                except ValueError as err:
                    # NOTE:
                    # Probably should return Not Found
                    # instead of raising error
                    raise ValidationError(
                        "Valid Plant id is required."
                    ) from err
                else:
                    return self.queryset.for_datapoint_list(plant_id)
            raise ValidationError("Plant id is required.")
        if self.action == "retrieve":
            return self.queryset.for_datapoint_retrieval()
        return super().get_queryset()


class ReportsViewSet(ListModelMixin, GenericViewSet):
    queryset = DataPoint.objects.select_related("plant").annotate_metrics()
    serializer_class = ReportsSerializer
    pagination_class = PageNumberPagination
    filter_backends = [
        ReportsFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["plant_name"]
    ordering_fields = ["plant_name"]
    ordering = ["plant_name"]
