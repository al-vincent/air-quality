from django.db import models

# Create your models here.
class Species(models.Model):
    name = models.TextField(default='')