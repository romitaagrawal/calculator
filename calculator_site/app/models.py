from django.db import models

# Create your models here.
class CalculatorHistory(models.Model):
    expression = models.CharField(max_length=255)
    result = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.expression} = {self.result}"