from django.shortcuts import render
from . import services

# Create your views here.
def index(request):
    data = services.SetupData()
    return render(request, "index.html", { "emission_types": data.emission_types(),
                                           "area_groups": data.area_groups(),
                                           "illness_types": data.illness_types() })