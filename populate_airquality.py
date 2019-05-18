##################################################################################
# This script is used to auto-populate django's automatically-generated sqlite 
# database (db.sqlite3). This reduces / negates the need for external 'mock-up'
# data for testing the app, and is a lot faster than updating the db via django's
# admin interface if more than a few items are to be added.
#
# When running the script, follow theses steps;
#  1. If there's an existing db.sqlite3 file (in the AirQuality project dir),
#       delete it.
#  2. In the shell, type the following:
#   $> python manage.py makemigrations      [Updates the models with any changes]
#   $> python manage.py migrate             [Creates the database schema]
#   $> python populate_airquality           [Runs this script to populate the db]
##################################################################################

# setting these environment variables before anything is run is *essential*!
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AirQuality.settings')

import django
django.setup()
from Emissions.models import LocalAuthority, Species, Site, HealthAdvice

import pandas as pd
import requests
import datetime as dt
from sys import exit

class PopulateDb():
    """
    Main class to populate the sqlite database. Add new methods to populate other
    tables as required.
    """
    def __init__(self, use_proxy=False, group='London'):
        """Determine whether or not to use the DES proxy required for DES, and 
            which grouping to use (default is London)"""
        self.group = group
        if use_proxy == True:
            self.proxy = {'http' : 'http://10.160.27.36:3128'}
        else:
            self.proxy = None
     
    def populate_local_authorities(self):
        """
        Get LocalAuthority (i.e. location) data from the LondonAir API and create 
        a LocalAuthority object for each item in the dict that's returned.

        If the API doesn't return a valid response, print a message to the console.
        
        """
        grp_url = "/Information/Groups/Json"
        la_url = "/Information/MonitoringLocalAuthority/GroupName=London/Json"
        grp_data = pd.DataFrame(self.get_data_from_API(grp_url)["Groups"]["Group"])
        la_data = pd.DataFrame(self.get_data_from_API(la_url)["LocalAuthorities"]["LocalAuthority"])
        if grp_data is not None and la_data is not None:
            df = la_data.merge(grp_data, left_on='@LocalAuthorityName', right_on='@Description')
            for item in df[["@LocalAuthorityName", "@LocalAuthorityCode", "@HomeURL", 
                            "@LaCentreLatitude", "@LaCentreLongitude"]].to_dict(orient="records"):
                la = LocalAuthority.objects.get_or_create(name=item["@LocalAuthorityName"],
                                                        code=item["@LocalAuthorityCode"],
                                                        latitude=item["@LaCentreLatitude"],
                                                        longitude=item["@LaCentreLongitude"],
                                                        link=item["@HomeURL"])[0]
                la.save()
        else:
            print("LondonAir API returned a 404 error for Local Authorities/ Groups")
    
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
    
    def populate_sites(self):
        """
        Get Site (i.e. measurement location) metadata from the LondonAir API and 
        create a Sites object for each item in the dict that's returned.

        If the API doesn't return a valid response, print a message to the console
        """
        data = self.get_data_from_API(f"/Information/MonitoringSiteSpecies/GroupName={self.group}/Json")
        if data is not None:
            for item in data['Sites']['Site']:
                try:
                    la = LocalAuthority.objects.get(name=item["@LocalAuthorityName"])
                
                    if item["@SiteCode"] != 'WMZ': #No lat/long info, site was only open
                                        #for three months in 2016, breaks everything else
                        
                        date_opened = dt.datetime.strptime(item["@DateOpened"], 
                                                                '%Y-%m-%d %H:%M:%S')
                        date_opened = date_opened.replace(tzinfo = dt.timezone.utc)
                        
                        if item["@DateClosed"] == '':
                            site_active = True
                            date_closed = None
                        else:    
                            site_active = False
                            date_closed = dt.datetime.strptime(item["@DateClosed"], 
                                                                '%Y-%m-%d %H:%M:%S')
                            date_closed = date_closed.replace(tzinfo = dt.timezone.utc)
                            
                        if type(item["Species"]) != list:
                            item_species = {item["Species"]["@SpeciesCode"] : 
                                            item["Species"]["@DateMeasurementFinished"]}    
                        else:
                            item_species = {i["@SpeciesCode"]: i['@DateMeasurementFinished'] 
                                            for i in item["Species"]}
                            
                        species_codes = ['CO', 'NO2', 'O3', 'PM10', 'PM25', 'SO2']
                        species_active = {i: False for i in species_codes}
                        for i in species_active:
                            if i in item_species.keys():
                                if item_species[i] == '':
                                    species_active[i] = True
                                            
                        sites = Site.objects.get_or_create(
                            name = item["@SiteName"],
                            code = item["@SiteCode"], 
                            site_type = item["@SiteType"],
                            local_auth = la,    # use the relevant LocalAuthority object
                            link = item["@SiteLink"],
                            latitude = float(item["@Latitude"]),
                            longitude = float(item["@Longitude"]),
                            site_date_open = date_opened,
                            site_date_closed = date_closed,
                            site_still_active = site_active,
                            co_measure_active = species_active["CO"],
                            no2_measure_active = species_active["NO2"],
                            o3_measure_active = species_active["O3"],
                            pm10_measure_active = species_active["PM10"],
                            pm25_measure_active = species_active["PM25"],
                            so2_measure_active = species_active["SO2"])[0]
                        
                        sites.save()
                except LocalAuthority.DoesNotExist:
                    print(f"Local Authority {item['@LocalAuthorityName']} not found")
        else:
            print("LondonAir API returned a 404 error for Sites")
    
    def populate_health_advice(self):
        """
        Get Health Advice Index data from the LondonAir API and create a 
        HealthAdvice object for each item in the dict that's returned.

        If the API doesn't return a valid response, print a message to the console
        """
        data = self.get_data_from_API("/Information/IndexHealthAdvice/json")
        if data is not None:
            hai_entries = data['AirQualityIndexHealthAdvice']['HealthAdvice']
            HAI = []
            for pair in range(1, len(hai_entries), 2):
                band_at_risk = hai_entries[pair-1]
                band_gen_pop = hai_entries[pair]
                common_keys = list(band_at_risk.keys())[:3]
                band_details = {i : band_at_risk[i] for i in common_keys}
                band_details[band_at_risk["@Group"]] = band_at_risk["@Advice"]
                band_details[band_gen_pop["@Group"]] = band_gen_pop["@Advice"]
                HAI.append(band_details)
            
            for item in HAI:
                advice = HealthAdvice.objects.get_or_create(
                            quality_band = item["@AirQualityBand"],
                            lower_index = item["@LowerAirQualityIndex"],
                            upper_index = item["@UpperAirQualityIndex"],
                            advice_gen_pop = item['General population'],
                            advice_at_risk = item['At-risk individuals'])[0]
                
                advice.save()
        else:
            print("LondonAir API returned a 404 error for Health Advice")
      
    def get_data_from_API(self, url):
        """
        Get data from the LondonAir API. If a connection cannot be made, print 
        a message to the console and exit.
        """
        root = "https://api.erg.kcl.ac.uk/AirQuality"
        try:
            response = requests.get(root + url, proxies = self.proxy)
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
    pd = PopulateDb(use_proxy=False, group='London')
    pd.populate_local_authorities()
    pd.populate_species()
    pd.populate_sites()
    pd.populate_health_advice()

if __name__ == "__main__":
    main()