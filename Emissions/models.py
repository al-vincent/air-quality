from django.db import models

class Species(models.Model):
    """
    A Species is a type of air emission / pollutant. The fields are copies
    of those provided in the LondonAir API.
    """
    name = models.TextField(default='')
    code = models.CharField(max_length=4, default='')
    description = models.TextField(default='')
    health_effect = models.TextField(default='')
    link = models.URLField(default='')

    def __str__(self):
        return f"{self.name} ({self.code}), {self.description}"

class Group(models.Model):
    """
    A Group is a geographic area (primarily in London) for which emissions 
    data is available. Fields are copies of those provided by the LondonAir API.
    """
    name = models.TextField(default='')
    description = models.TextField(default='')
    link = models.URLField(default='')

    def __str__(self):
        return f"{self.name}, {self.description} ({self.link})"

class HealthAdvice(models.Model):
    pass

class Objective(models.Model):
    pass