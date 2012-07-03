from django.db import models

class EuroToUSD(models.Model):
    date = models.DateField('date')
    rate = models.DecimalField(max_digits=10, decimal_places=5)

class EuroToGBP(models.Model):
    date = models.DateField('date')
    rate = models.DecimalField(max_digits=10, decimal_places=5)

