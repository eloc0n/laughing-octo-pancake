from django.db.models import Q
from rest_framework import filters


class ReportsFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if start_datetime := request.query_params.get("start_datetime"):
            queryset = queryset.filter(datetime__gte=start_datetime)
        if end_datetime := request.query_params.get("end_datetime"):
            queryset = queryset.filter(datetime__lte=end_datetime)

        show_archived = (
            request.query_params.get("show_archived", "false").lower()
            == "true"
        )
        if show_archived:
            queryset = queryset.filter(
                Q(plant__is_archived=False) | Q(plant__is_archived=True)
            )
        else:
            queryset = queryset.filter(plant__is_archived=False)

        return queryset
