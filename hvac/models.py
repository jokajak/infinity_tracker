from django.db import models


# Create your models here.
class HVAC(models.Model):
    serial = models.CharField(max_length=100)
