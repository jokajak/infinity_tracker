"""HVAC models."""
from django.db import models


class ActivityChoices(models.IntegerChoices):
    """HVAC Activity Choices."""

    HOME = 1
    SLEEP = 2
    AWAY = 3
    AWAKE = 4
    MANUAL = 5


class FanChoices(models.IntegerChoices):
    """HVAC Fan Choices."""

    low = 1


class ZoneConditioningChoices(models.IntegerChoices):
    """HVAC ZoneConditioning Choices."""

    low = 1


class HVAC(models.Model):
    """HVAC Model."""

    serial = models.CharField(max_length=100)
    heat_set_point = models.DecimalField(max_digits=5, decimal_places=2)
    cool_set_point = models.DecimalField(max_digits=5, decimal_places=2)
    # activity = models.IntegerChoices(choices=HVACActivities.choices)
    # activity = models.Choices(


#        "enabled": None,
#        "currentActivity": "activity",
#        "rt": "temp",
#        "rh": "humidity",
#        "fan": "fan",
#        "hold": "hold",
#        "name": None,
#        "otmr": None,


class Zone(models.Model):
    """HVAC Zone model.

    <zone id="1">
      <name>ZONE 1</name>
      <enabled>on</enabled>
      <currentActivity>home</currentActivity>
      <rt>76.0</rt>
      <rh>59</rh>
      <fan>low</fan>
      <htsp>70.0</htsp>
      <clsp>76.0</clsp>
      <hold>off</hold>
      <otmr/>
      <zoneconditioning>idle</zoneconditioning>
      <damperposition>15</damperposition>
    </zone>
    """

    id = models.PositiveIntegerField()
    name = models.CharField()
    enabled = models.BooleanField()
    current_activity = models.IntegerChoices(choices=ActivityChoices)
    current_temp = models.DecimalField(max_digits=5, decimal_places=2)
    current_humidity = models.PositiveIntegerField()
    fan = models.IntegerChoices(choice=FanChoices)
    heat_set_point = models.DecimalField(max_digits=5, decimal_places=2)
    cool_set_point = models.DecimalField(max_digits=5, decimal_places=2)
    hold = models.CharField()
    otmr = models.CharField()
    zone_conditioning = models.IntegerChoices(choices=ZoneConditioningChoices)
    damper_position = models.PositiveIntegerField()
