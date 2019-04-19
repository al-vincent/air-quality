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

class AirQualityApiData:
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

    def process_group_emissions(self, group_data, field1, field2):
        output_data = []
        for la in group_data[field1][field2]:
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

    def get_current_emissions_across_london(self, group_name="London"):
        """
        Get current emissions values for all London sites (no interpolation), for 
        all emissions types
        """
        URL = f"/Hourly/MonitoringIndex/GroupName={group_name}/Json"
        data = self.get_data_from_API(URL)
        if data is not None:
            return self.process_group_emissions(data, 'HourlyAirQualityIndex', 'LocalAuthority')
        else:
            return None

    def get_emissions_across_london_last_n_days(self, group_name="London", n=7):
        # I want to: 
        # - get emissions for the last n days, i.e. today and the preceeding 6 days
        # - average the emissions (for each emission), by local auth and also across London
        #   -- can the be done more efficiently on the client-side?
        # Notes:
        # - the URL I need is /Daily/MonitoringIndex/GroupName={Group}/Date={Date}/Json
        # - the output format is very similar to that for get_current_emissions_across_london :-)
        output_data = {}
        for i in range(1, n):
            day = datetime_obj_to_str(dt.datetime.now() - dt.timedelta(days = i))
            if day[0] == "0": day = day[1:]            
            URL = f"/Daily/MonitoringIndex/GroupName={group_name}/Date={day}/Json"
            data = self.get_data_from_API(URL)            
            if data is not None:
                output_data[day] = self.process_group_emissions(data, "DailyAirQualityIndex", "LocalAuthority")
            else:
                output_data[day] = None
        
        return output_data

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

    def get_all_emissions_info(self):
        """
        Get information about each of the emissions types; name, code, description, its effect on health, 
        a link to more information on the emission.

        Return a json-style list of dicts, where each list item is a particular emissions type, e.g.:
        [{"SpeciesName": "Carbon Monoxide", "SpeciesCode": "CO", "Description": "..<text>..", "HealthEffect":"..<text>..", "Link": "www..."},
         {"SpeciesName": "Ozone", "SpeciesCode": "O3", "Description": "..<text>..", "HealthEffect":"..<text>..", "Link": "www..."},
         ...]
        """
        URL = f"/Information/Species/Json"
        data = self.get_data_from_API(URL)
        if data is not None:
            species_info = data['AirQualitySpecies']['Species']
            keys = list(species_info[0].keys())
            return [{k.strip('@') : species[k] for k in keys} for species in species_info]
        else:
            return None

    def illness_types(self):
        return [{"value": "asthma", "text":"Asthma"},
                {"value": "emphesema", "text":"Emphesema"}]

def main():
    setup = AirQualityApiData(use_DES_proxy = False)

    ldn = setup.get_current_emissions_across_london()
    df = pd.DataFrame(ldn)
    print("\nEmissions across London\n-----------------------")
    print(df.head())

    e = setup.get_all_emissions_info()
    df = pd.DataFrame(e)
    print("\nEmissions info\n--------------")
    print(df.head())

    last_n = setup.get_emissions_across_london_last_n_days(n=3)
    print("\nLast n days:\n===========")
    for day in last_n:
        print(f"\n{day}\n{'-'*len(day)}")
        print(pd.DataFrame(last_n[day]).head())
    
if __name__ == "__main__":
    main()
    