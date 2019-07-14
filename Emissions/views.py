from django.shortcuts import render
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from Emissions.services import AirQualityApiData
from Emissions.models import LocalAuthority, Species, Site

from json import load
import os

def index(request):
    """
    Get data from the database / LondonAir API and pass it to the html page.
    """
    # get config file data from static/js/config.json
    with open(os.path.join(settings.STATIC, 'js/config.json'), "r") as f:
        config = load(f)
    # get placeholder data
    data = AirQualityApiData()    
    # get a list of London local authorities from db
    local_auths = list(LocalAuthority.objects.all().values())  
    # get a list of sites from the db
    sites = list(Site.objects.all().values())
    # get a list of species from db
    species = list(Species.objects.all().values())
    return render(request, "Emissions/index.html", {"config": config,
                                                    "emissions_info": species,
                                                    "local_auths": local_auths,
                                                    "sites": sites,
                                                    "illness_types": data.illness_types(), 
                                                    "emissions_data": data.get_current_emissions_across_london()})