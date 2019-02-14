from django.shortcuts import render
from Emissions.services import SetupData

def index(request):
    """
    Get dummy data from services.py, pass this to the index.html page to render
    (populates the drop-down menus)
    """
    data = SetupData()
    return render(request, "index.html", { "emission_types": data.emission_types(),
                                           "area_groups": data.area_groups(),
                                           "illness_types": data.illness_types() })