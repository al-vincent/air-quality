from django.shortcuts import render
from Emissions.services import AirQualityApiData
from Emissions.models import Group, Species

def index(request):
    """
    Get dummy data from services.py, pass this to the index.html page to render
    (populates the drop-down menus)
    """
    # get placeholder data
    data = AirQualityApiData()    
    # get a list of groups from db, removing the first 12 (non-London)
    grps = [{"value":grp.name, "text":grp.description} for grp in Group.objects.all().filter(id__gt=11)]
    # get a list of species from db
    species = [{"value":sp.code, "text":sp.name} for sp in Species.objects.all()]
    return render(request, "Emissions/index.html", {"emission_types": species,
                                                    "emissions_info": data.get_all_emissions_info(),
                                                    "area_groups": grps,
                                                    "illness_types": data.illness_types(), 
                                                    "geo_data": data.get_current_emissions_across_london()})