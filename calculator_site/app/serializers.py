from rest_framework import serializers
from .models import CalculatorHistory

class CalculatorHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculatorHistory
        fields = ('id', 'expression', 'result', 'timestamp')