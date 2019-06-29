from django.shortcuts import render
from Emissions.services import AirQualityApiData
from Emissions.models import LocalAuthority, Species, Site

def index(request):
    """
    Get data from the database / LondonAir API and pass it to the html page.
    """
    # get placeholder data
    data = AirQualityApiData()    
    # get a list of London local authorities from db
    local_auths = list(LocalAuthority.objects.all().values())  
    # get a list of sites from the db
    sites = list(Site.objects.all().values())
    # get a list of species from db
    species = list(Species.objects.all().values())
    return render(request, "Emissions/index.html", {"emissions_info": species,
                                                    "local_auths": local_auths,
                                                    "sites": sites,
                                                    "illness_types": data.illness_types(), 
                                                    "emissions_data": data.get_current_emissions_across_london()})