from django.db import models

# Create your models here.
class Species(models.Model):
    name = models.TextField(default='')
    code = models.CharField(max_length=4, default='')
    description = models.TextField(default='')
    health_effect = models.TextField(default='')
    link = models.TextField(default='')

    def __str__(self):
        return f"{self.name} ({self.code}), {self.description}"

class Group(models.Model):
    name = models.TextField(default='')
    description = models.TextField(default='')
    link = models.TextField(default='')

    def __str__(self):
        return f"{self.name}, {self.description} ({self.link})"

class HealthAdvice(models.Model):
    pass

class Objective(models.Model):
    pass