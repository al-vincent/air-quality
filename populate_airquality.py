import os
import requests

class PopulateDb():
    def populate_groups(self):
        data = self.get_data_from_API("/Information/Groups/Json")
        if data is not None:
            for item in data["Groups"]["Group"]:
                grp = Group.object.create(name=item["@GroupName"],
                                          description=item["@Description"],
                                          link=item["@WebsuteURL"])
                grp.save()
    
    def populate_species(self):
        data = self.get_data_from_API("/Information/Species/Json")
        if data is not None:
            for item in data["AirQualitySpecies"]["Species"]:
                species = Species.object.create(name=item["@SpeciesName"],
                                                code=item["@SpciesCode"],
                                                description=item["@Description"],
                                                health_effect=item["@HealthEffect"],
                                                link=item["@Link"])
                species.save()
    
    def get_data_from_API(self, url):
        root = "http://api.erg.kcl.ac.uk/AirQuality"
        response = requests.get(root + url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

def main():    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AirQuality.settings')
    from Emissions.models import Group, Species
    pd = PopulateDb()
    pd.populate_groups()
    pd.populate_species()


if __name__ == "__main__":
    main()