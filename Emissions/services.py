# TODOs:
# - Update any methods where the return-type is a Pandas dataframe, to either a 
#   dict or JSON
#   -- Consider; do we need Pandas at all here? Can we only import it to specific fncs?
# - Make sure every function returns *something*
# - Get rid of all '@'s in returns; just weird and confusing
# - More generally; for our app, would be more DRY to have a config file containing 
#   mappings of API headers to variable names, that we can use across the app?
#   -- Could it go into settings.py? Need to check we're not accidentally overriding 
#       reserved names!
# - Will need a method that takes a site (or list of sites), an emission type and a 
#   date-range and returns the relevant intensity
# - Setup logging (e.g. when the API isn't available)

import datetime as dt
import requests
import pandas as pd

BASE_URL = "http://api.erg.kcl.ac.uk/AirQuality"
DES_PROXY = {'http' : 'http://10.160.27.36:3128'}
DEFAULT_START_DATE = "01Jan2019"
MAX_INDEX = 10

def datetime_obj_to_str(dt_obj):
    """
    Converts a python datetime object to the format used within the LondonAir API.

    Parameters:
    - dt_obj (python datetime object), a datetime to be converted

    Returns:
    - string of format DDMonYYY (i.e. 01Jan2000)
    """
        
    return dt_obj.strftime('%d%b%Y')

DEFAULT_END_DATE =  datetime_obj_to_str(dt.datetime.now() + dt.timedelta(days = 1))

class SetupData():
    """
    Series of methods to return API data to the application. Call SetupData 
    class with boolean True/False to use the required DES proxy server.
    """
    
    def __init__(self, use_DES_proxy=False):
        # *********************
        # AV: Luke - this use_DES_proxy var is a good idea, and works well for DES (obvs!).
        # A more general case though would be to replace the boolean flag with a setting for 
        # users who are behind *any* proxy; we could also build a simple interface to let 
        # them enter the details...?
        # *********************
        if use_DES_proxy == True:
            self.proxy = DES_PROXY
        else:
            self.proxy = None
    
    def get_data_from_API(self, url, proxy=None):
        """
        Get data from the LondonAir API. If a connection cannot be made, print 
        a message to the console and exit.

        Parameters:
        - url (str), the URL containing the API data
        - proxy (str), a URL containing the address of a proxy server. Optional, default None

        Returns:
        - a JSON structure containing the data provided by the API; or None if the request 
        failed (e.g. due to a connection error, or an error with the URL provided)
        """
        
        try:
            response = requests.get(BASE_URL + url, proxies=proxy)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.ConnectionError:
            # placeholder at present; ideally; this would be logged to file (rather than 
            # printed to console).
            print(f"\n*** No response from {BASE_URL + url}; is the URL correct? ***\n")
            return None
    
    def setup_row_dict(self, site_data, la_name):
        return {"Local Authority name": la_name, 
                "Site name": site_data["@SiteName"],
                "Site code": site_data["@SiteCode"], 
                "Site type": site_data["@SiteType"], 
                "Date": site_data["@BulletinDate"], 
                "Latitude": float(site_data["@Latitude"]), 
                "Longitude": float(site_data["@Longitude"]), 
                "Carbon Monoxide": None, 
                "Nitrogen Dioxide": None, 
                "Sulphur Dioxide": None, 
                "Ozone": None, 
                "PM10 Particulate": None, 
                "PM2.5 Particulate": None}
    
    def convert_values(self, value):
        if value == 0 or value == None:
            return None
        else:
            return ((MAX_INDEX - value) + 1) / MAX_INDEX

    def get_species_type(self, species_info, row):
        if species_info["@SpeciesCode"] == "CO":
            row["Carbon Monoxide"] = self.convert_values(float(species_info["@AirQualityIndex"]))
        elif species_info["@SpeciesCode"] == "NO2":
            row["Nitrogen Dioxide"] = self.convert_values(float(species_info["@AirQualityIndex"]))
        elif species_info["@SpeciesCode"] == "SO2":
            row["Sulphur Dioxide"] = self.convert_values(float(species_info["@AirQualityIndex"]))
        elif species_info["@SpeciesCode"] == "O3":
            row["Ozone"] = self.convert_values(float(species_info["@AirQualityIndex"]))
        elif species_info["@SpeciesCode"] == "PM10":
            row["PM10 Particulate"] = self.convert_values(float(species_info["@AirQualityIndex"]))
        elif species_info["@SpeciesCode"] == "PM25":
            row["PM2.5 Particulate"] = self.convert_values(float(species_info["@AirQualityIndex"]))
        else:
            print(f"\n*** Unexpected species {species_info['@SpeciesCode']} ***\n")
        return row

    def update_site_species_info(self, site, row):
        # check to make sure the site actually does collect some sort of emissions
        if "Species" in site:
            # some sites collect several emission types; will get a list of dicts
            if isinstance(site["Species"], list) and row is not None:
                for species in site["Species"]:
                    row = self.get_species_type(species, row)
            # if only one emission type is collected, will get a dict
            elif isinstance(site["Species"], dict):
                row = self.get_species_type(site["Species"], row)
            # something's gone wrong...
            else:
                print(f"\n*** Unexpected species type: species info = {species}, {type(species)} ***\n")
                row = None
        # odd behaviour, worth checking the source JSON
        else:
            print(f"\n*** Site {site} has no Species - is this correct? ***\n")
            row = None

        return row

    def get_emissions_across_london(self, group_name="London"):
        """
        Get current emissions values for all London sites (no interpolation), for 
        all emissions types
        """
        URL = f"/Hourly/MonitoringIndex/GroupName={group_name}/Json"
        data = self.get_data_from_API(URL)
        output_data = []
        if data is not None:
            for la in data['HourlyAirQualityIndex']['LocalAuthority']:
                # some local authorities don't actually have any collection sites
                if 'Site' in la:
                    # print(la["@LocalAuthorityName"])
                    # case where the LA has more than 1 collection site
                    if isinstance(la['Site'], list):
                        for site in la['Site']:
                            row = self.setup_row_dict(site, la["@LocalAuthorityName"]) 
                            output_data.append(self.update_site_species_info(site, row))
                    # case where the LA has exactly 1 collection site
                    elif isinstance(la['Site'], dict):
                        site = la['Site']       # don't really need this, but for consistency with above
                        row = self.setup_row_dict(site, la["@LocalAuthorityName"])
                        output_data.append(self.update_site_species_info(site, row))
                    # something's gone wrong...!
                    else:
                        row = None
                        print(f"Unexpected site type: site info = {site}, {type(site)}")                        
            
            return output_data
        else:
            return None

    def get_hourly_site_readings_between(self, site_code, 
                                         start_date=DEFAULT_START_DATE, 
                                         end_date=DEFAULT_END_DATE):
        """
        Provides measurements of all particulates for a specific sites on an hourly basis,
        over a defined time window.
        
        Parameters:
        - site_code (str), a 3(?)-character code for the site that's being queried, e.g. 'TDO'
        - start_date (str), the start date of the time window we want data for. Format is 
        DDMonYYYY, e.g. 01Jan2000. Optional; default is 01Jan2019.
        - end_date (str), the end date of the time window we want data for. Format is 
        DDMonYYYY, e.g. 01Jan2000. Optional; default is the current date.
        
        Returns:
        - a pandas Dataframe of the species measurements across the 
        datetime hours requested.

        Note: conversion to the correct format can be done via the datetime_obj_to_str
        convenience function.
        """        
        URL = f"/Data/Site/SiteCode={site_code}/StartDate={start_date}/EndDate={end_date}/Json"
        data = self.get_data_from_API(URL)
        if data is not None:
            df = pd.DataFrame(data['AirQualityData']['Data'])
            # reshape the datat into a more useful format
            df = df.pivot(index='@MeasurementDateGMT', columns="@SpeciesCode", values="@Value").reset_index()
            # get rid of @s in the column names
            return df.rename(index=str, columns={'@MeasurementDateGMT':'MeasurementDate'}).to_dict('records')    
        else:
            return None    
    
    def get_daily_index_latest(self, site_code):
        """
        Provides the most current health index rating for a particular site. 

        Parameters:
        - site_code (str), a 3(?)-digit code for the site that's being queried.
        
        Returns: 
        - Pandas DataFrame of the different species measured at that 
        site. Includes the most current index, which band that falls under, the 
        index source, the species code, and the species name.
        """
        
        URL = f"/Daily/MonitoringIndex/Latest/SiteCode={site_code}/Json"
        data = self.get_data_from_API(URL, self.proxy)
        if data is not None:
            daily_index_latest = (data['DailyAirQualityIndex']['LocalAuthority']
                                    ["Site"]["Species"])
            
            keys = list(daily_index_latest[0].keys())
            daily_index_latest = [{k.strip('@') : species[k] for k in keys} 
                                    for species in daily_index_latest]
            return daily_index_latest
        else:
            return None
            
    def get_daily_index_on_date(self, site_code, date):
        """
        Gets the hourly particulate measurements for a given date. 
        
        Format for dates is 
        DDMonYYYY (01Jan2000); conversion of datetime objects can be done with 
        the datetime_obj_to_str() func.

        Parameters:
        - site_code (str), a 3(?)-character code for the site that's being queried, e.g. 'TDO'
        - date (str), the start date of the time window we want data for. Format is 
        DDMonYYYY, e.g. 01Jan2000. Optional; default is 01Jan2019.
                
        Returns: 
            a pandas DataFrame of each of the different species measured at that site. 
            Includes the most current index, which band that falls under, the index source, 
            the species code, and the species name.

        Note: conversion to the correct format can be done via the datetime_obj_to_str
        convenience function.
        """
        
        if type(date) == dt.datetime:
            date = datetime_obj_to_str(date)
        URL = f"/Daily/MonitoringIndex/SiteCode={site_code}/Date={date}/Json"
        data = self.get_data_from_API(URL, self.proxy)
        if data is not None:
            daily_index_dated = (data['DailyAirQualityIndex']['LocalAuthority']
                                ["Site"]["Species"])
            keys = list(daily_index_dated[0].keys())
            daily_index_dated = [{k.strip('@') : species[k] for k in keys} 
                                    for species in daily_index_dated]
            return daily_index_dated
        else:
            return None                

    def nowcast(self, lat, long):
        """
        For a specific point, will get data from the nearest emissions collection 
        points and interpolate to provide an estimate of the emissions at that point.

        Parameters:
            - lat (float), a decimal(?) latitude value
            - long (float), a decimal(?) longitude value
        
        Returns:
        - a dictionary with keys:
        ['@lat', '@lon', '@Easting', '@Northing', '@NO2_Annual', '@O3_Annual', 
        '@PM10_Annual', '@PM25_Annual', '@NO2', '@O3', '@PM10', '@PM25', 
        '@NO2_Index', '@O3_Index', '@PM10_Index', '@PM25_Index', '@Max_Index']
        """
        URL = f"/Data/Nowcast/lat={lat}/lon={long}/Json"
        data = self.get_data_from_API(URL)
        # TODO: get rid of '@' symbols in return dict
        if data is not None:
            return data['PointResult']
        else:
            return None

    def emission_types(self):
        #need to replace call in templates/Emissions/index.html
        return [{"value": "carbon-monoxide", "text":"Carbon Monoxide"},
                {"value": "nitrogen-dioxide", "text":"Nitrogen Dioxide"}]
        
    def area_groups(self):
        #need to replace call in templates/Emissions/index.html
        return [{"value": "all", "text": "All"},
                {"value": "barnet", "text": "Barnet"}]
    
    def illness_types(self):
        return [{"value": "asthma", "text":"Asthma"},
                {"value": "emphesema", "text":"Emphesema"}]

class GetEmissionsData():
    """
    Provde lat/long/emission intensity values for a series of emission types.
    Again, dummy data used for testing.
    """
    def __init__(self):    
        self.emission_types = [
            {"lat":51.30295525,"lng":-0.24772238333,"CO":0.331566754675031,"NO2":1},
            {"lat":51.3155634,"lng":-0.247150915,"CO":0.0553410958886463,"NO2":1},
            {"lat":51.3077980667,"lng":-0.24749606833,"CO":0.0892525576065953,"NO2":1},
            {"lat":51.3024718333,"lng":-0.247689145,"CO":0.590075732442714,"NO2":1},
            {"lat":51.3010265333,"lng":-0.24781286667,"CO":0.15434154031539,"NO2":1},
            {"lat":51.3051546167,"lng":-0.24761810167,"CO":0.545913378087492,"NO2":1},
            {"lat":51.3027743667,"lng":-0.24772973,"CO":0.633489041919876,"NO2":1},
            {"lat":51.3113692333,"lng":-0.24732625,"CO":0.266503161072438,"NO2":1},
            {"lat":51.3061175,"lng":-0.24761095667,"CO":0.276762853991245,"NO2":1},
            {"lat":51.3126536833,"lng":-0.24718492,"CO":0.1891805552013,"NO2":1},
            {"lat":51.49984655,"lng":-0.247884775,"CO":0.0675455473384583,"NO2":1},
            {"lat":51.4996625,"lng":-0.24783593833,"CO":0.0330886810539454,"NO2":1},
            {"lat":51.3096838,"lng":-0.24734820333,"CO":0.555126115173718,"NO2":1},
            {"lat":51.3163971333,"lng":-0.24703382333,"CO":0.825905559386503,"NO2":1},
            {"lat":51.3019659333,"lng":-0.247801565,"CO":0.96350573450757,"NO2":1},
            {"lat":51.3017677,"lng":-0.24778972667,"CO":0.655546251121835,"NO2":1},
            {"lat":51.3082934833,"lng":-0.24747193,"CO":0.668460695656423,"NO2":1},
            {"lat":51.3124935167,"lng":-0.24721662833,"CO":0.62742638749223,"NO2":1},
            {"lat":51.3112822667,"lng":-0.24727057,"CO":0.488621588652691,"NO2":1},
            {"lat":51.3088314833,"lng":-0.24744561333,"CO":0.761584090132723,"NO2":1},
            {"lat":51.3140193667,"lng":-0.24723065,"CO":0.893369510759159,"NO2":1},
            {"lat":51.3151048833,"lng":-0.24715047667,"CO":0.330237470617188,"NO2":1},
            {"lat":51.3155721667,"lng":-0.24712705333,"CO":0.846069812688032,"NO2":1},
            {"lat":51.31564375,"lng":-0.24698925833,"CO":0.382826719439399,"NO2":1},
            {"lat":51.3157315333,"lng":-0.24712060333,"CO":0.0212573374476552,"NO2":1},
            {"lat":51.3158956833,"lng":-0.24711298667,"CO":0.495373866646281,"NO2":1},
            {"lat":51.3044821667,"lng":-0.24765082167,"CO":0.802100320556479,"NO2":1},
            {"lat":51.3045073333,"lng":-0.24759204333,"CO":0.766882008309998,"NO2":1},
            {"lat":51.3046759167,"lng":-0.24758561667,"CO":0.970506803458753,"NO2":1},
            {"lat":51.4983034667,"lng":-0.24792230333,"CO":0.17487089909492,"NO2":1},
            {"lat":51.4987899833,"lng":-0.24796567167,"CO":0.560477608746508,"NO2":1}
        ]

def main():
    setup = SetupData(use_DES_proxy = False)
    ldn = setup.get_emissions_across_london()
    df = pd.DataFrame(ldn)
    print(df.head())
    print(f"Min lat: {df['Latitude'].min()}, Max lat: {df['Latitude'].max()}")
    print(f"Min lng: {df['Longitude'].min()}, Max lng: {df['Longitude'].max()}")
    
if __name__ == "__main__":
    main()
    