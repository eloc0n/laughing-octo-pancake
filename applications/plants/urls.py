from rest_framework.routers import DefaultRouter

from .viewsets import PlantDataPointViewSet, PlantViewSet, ReportsViewSet

router = DefaultRouter()
router.register(r"plants", PlantViewSet, basename="plants")
router.register(
    r"plants/(?P<plant_id>[-\w]+)/datapoints",
    PlantDataPointViewSet,
    basename="datapoints",
)
router.register(r"reports", ReportsViewSet, basename="reports")
urlpatterns = router.urls
