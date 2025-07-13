from rest_framework import serializers
from . import models

class commentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.comment
        fields = '__all__'
        extra_kwargs = dict(parent=dict(write_only=True))
