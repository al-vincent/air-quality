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


class LocalAuthority(models.Model):
    """
    A LocalAuthority is a London Local Authority, i.e. a geographic and 
    administrative area in London. 

    Each LA contains Sites that collect the actual emissions data. The model
    contains lat/lon properties; these represent the *centre* of the LA, 
    rather than the whole area.
    """
    name = models.TextField(default='')
    code = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    link = models.URLField(default='', null=True, blank=True)

    def __str__(self):
        return f"{self.name}, {self.code} ({self.link})"
    
    
class Site(models.Model):
    """
    A site is a specific measuring station for which emissions data is 
    available. Many sites make up a group. Fields are copies of those provided 
    by the LondonAir API, with unecessary fields chopped out.
    """
    name = models.TextField(default='')
    code = models.CharField(max_length=3, default='')
    site_type = models.TextField(default='')
    local_auth = models.ForeignKey(LocalAuthority, on_delete=models.CASCADE)
    link = models.URLField(default='')
    latitude = models.FloatField(default='')
    longitude = models.FloatField(default='')
    site_still_active = models.BooleanField(default=False)
    site_date_open = models.DateTimeField(null=True, blank=True)
    site_date_closed = models.DateTimeField(null=True, blank=True)
    
    co_measure_active = models.BooleanField(default=False)
#    co_measure_start = models.DateTimeField(default='')
#    co_measure_end = models.DateTimeField(default='')
    no2_measure_active = models.BooleanField(default=False)
#    no2_measure_start = models.DateTimeField(default='')
#    no2_measure_end = models.DateTimeField(default='')
    o3_measure_active = models.BooleanField(default=False)
#    o3_measure_start = models.DateTimeField(default='')
#    o3_measure_end = models.DateTimeField(default='')
    pm10_measure_active = models.BooleanField(default=False)
#    pm10_measure_start = models.DateTimeField(default='')
#    pm10_measure_end = models.DateTimeField(default='')
    pm25_measure_active = models.BooleanField(default=False)
#    pm25_measure_start = models.DateTimeField(default='')
#    pm25_measure_end = models.DateTimeField(default='')
    so2_measure_active = models.BooleanField(default=False)
#    so2_measure_start = models.DateTimeField(default='')
#    so2_measure_end = models.DateTimeField(default='')

    def __str__(self):
        return f"{self.name} ({self.code}), {self.local_auth}"


class HealthAdvice(models.Model):
    quality_band = models.TextField(max_length = 9, default = '')
    lower_index = models.IntegerField(null = True, default = None)
    upper_index = models.IntegerField(null = True, default = None)
    advice_gen_pop = models.TextField(default='')
    advice_at_risk = models.TextField(default='')
    
    def __str__(self):
        return f"{self.quality_band}, {self.lower_index} - {self.upper_index}"

class Objective(models.Model):
    """Return from the objectives call has a variable number of entries for 
    different pollutants. Suggest implementing subclasses for each pollutant,
    before tying them all together with a singular Objective class using 
    multi-table inheritance. 
    
    Other alternative solns are to have the first entry in the table containing 
    the first objective for each pollutant, the second containing the second 
    (and so on), before filling in NULL entries for those where no subsequent 
    objective exists"""

    pass