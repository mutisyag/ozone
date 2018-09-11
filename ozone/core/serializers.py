from rest_framework.exceptions import ValidationError
from rest_framework import serializers
#from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from .models import Region, Subregion, Party, Submission, Article7Questionnaire


class RegionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Region
        fields = ('name', 'abbr')


class SubregionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Subregion
        fields = ('name', 'abbr', 'region')


class PartySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Party
        fields = ('name', 'abbr', 'subregion')
