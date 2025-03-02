class SerializerActionClassMixin(object):
    def get_serializer_class(self):
        """
        A class which inhertis this mixins should have variable
        `serializer_action_classes`.
        Look for serializer class in self.serializer_action_classes, which
        should be a dict mapping action name (key) to serializer class (value).
        In case an action has a mode definition nested mapping should also
        exist.
        i.e.:
        class SampleViewSet(viewsets.ViewSet):
            serializer_class = Serializer
            serializer_action_classes = {
               'action-x': ActionXDefaultSerializer,
               'action-y': ActionYDefaultSerializerr,
            }
        If there's no entry for that action then just fallback to the regular
        get_serializer_class lookup: self.serializer_class, DefaultSerializer.
        """
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()
