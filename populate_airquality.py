# setting these environment variables before anything is run is *essential*!
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AirQuality.settings')

import django
django.setup()
from Emissions.models import Group, Species

import requests
from sys import exit


class PopulateDb():
    """
    Main class to populate the sqlite database. Add new methods to populate other
    tables as required.
    """
    def populate_groups(self):
        """
        Get Group (i.e. location) data from the LondonAir API and create a Group
        object for each item in the dict that's returned.

        If the API doesn't return a valid response, print a message to the console
        """
        data = self.get_data_from_API("/Information/Groups/Json")
        if data is not None:
            for item in data["Groups"]["Group"]:
                grp = Group.objects.get_or_create(name=item["@GroupName"],
                                                description=item["@Description"],
                                                link=item["@WebsiteURL"])[0]
                grp.save()
        else:
            print("LondonAir API returned a 404 error for Groups")
    
    def populate_species(self):
        """
        Get Species (i.e. emission) data from the LondonAir API and create a Species
        object for each item in the dict that's returned.

        If the API doesn't return a valid response, print a message to the console
        """
        data = self.get_data_from_API("/Information/Species/Json")
        if data is not None:
            for item in data["AirQualitySpecies"]["Species"]:
                species = Species.objects.get_or_create(name=item["@SpeciesName"],
                                                    code=item["@SpeciesCode"],
                                                    description=item["@Description"],
                                                    health_effect=item["@HealthEffect"],
                                                    link=item["@Link"])[0]
                species.save()
        else:
            print("LondonAir API returned a 404 error for Species")
    
    def get_data_from_API(self, url):
        """
        Get data from the LondonAir API. If a connection cannot be made, print 
        a message to the console and exit.
        """
        root = "https://api.erg.kcl.ac.uk/AirQuality"
        try:
            response = requests.get(root + url)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.ConnectionError:
            print("No response from LondonAir API server")
            exit(1)       

def main(): 
    """
    Driver function
    """
    pd = PopulateDb()
    pd.populate_groups()
    pd.populate_species()

if __name__ == "__main__":
    main()