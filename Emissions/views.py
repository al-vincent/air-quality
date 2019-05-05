from django.shortcuts import render
from Emissions.services import AirQualityApiData
from Emissions.models import LocalAuthority, Species

def index(request):
    """
    Get dummy data from services.py, pass this to the index.html page to render
    (populates the drop-down menus)
    """
    # get placeholder data
    data = AirQualityApiData()    
    # get a list of groups from db, removing the first 12 (non-London)
    local_auths = [{"value":la.name, "text":la.name} for la in LocalAuthority.objects.all()]
    # get a list of species from db
    species = [{"value":sp.code, "text":sp.name} for sp in Species.objects.all()]
    return render(request, "Emissions/index.html", {"emission_types": species,
                                                    "emissions_info": data.get_all_emissions_info(),
                                                    "area_groups": local_auths,
                                                    "illness_types": data.illness_types(), 
                                                    "geo_data": data.get_current_emissions_across_london()})