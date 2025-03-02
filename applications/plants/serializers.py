from rest_framework import serializers

from .models import Plant


class PlantSerializer(serializers.ModelSerializer):
    """
    Serializer for Plant model.
    """

    name = serializers.CharField()

    class Meta:
        model = Plant
        fields = [
            "id",
            "name",
        ]

        read_only_fields = [
            "id",
        ]

    def validate_name(self, value):
        if Plant.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                "A plant with this name already exists."
            )
        return value


class DataPointSerializer(serializers.Serializer):
    """
    Display of data points.
    """

    id = serializers.CharField()
    energy_expected = serializers.FloatField()
    energy_observed = serializers.FloatField()
    irradiation_expected = serializers.FloatField()
    irradiation_observed = serializers.FloatField()
    datetime = serializers.DateTimeField()


class PlantDataPointSerializer(DataPointSerializer):
    """
    Display of plants with datapoints.
    """

    plant_id = serializers.CharField()
    plant_name = serializers.CharField()


class ReportsSerializer(serializers.Serializer):
    plant_name = serializers.CharField()
    energy_expected_sum = serializers.FloatField()
    energy_observed_sum = serializers.FloatField()
    energy_expected_avg = serializers.FloatField()
    energy_observed_avg = serializers.FloatField()
    energy_efficiency = serializers.FloatField()
    irradiation_expected_sum = serializers.FloatField()
    irradiation_observed_sum = serializers.FloatField()
    irradiation_expected_avg = serializers.FloatField()
    irradiation_observed_avg = serializers.FloatField()
    irradiation_efficiency = serializers.FloatField()


class MonitoringServiceSerializer(serializers.Serializer):
    datetime = serializers.DateTimeField()
    expected = serializers.DictField(child=serializers.FloatField())
    observed = serializers.DictField(child=serializers.FloatField())
