from django.contrib import admin

from Emissions.models import Species, LocalAuthority, Site, HealthAdvice

# Register your models here.
admin.site.register(Species)
admin.site.register(LocalAuthority)
admin.site.register(Site)
admin.site.register(HealthAdvice)