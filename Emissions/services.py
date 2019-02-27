import requests, datetime as dt, pandas as pd

BASE_URL = "http://api.erg.kcl.ac.uk/AirQuality"
DES_PROXY = {'http' : 'http://10.160.27.36:3128'}  


def datetime_obj_to_str(dt_obj):
    """Converts a python datetime object to the format used within the 
        API calls : Returns string of format DDMonYYY (i.e. 01Jan2000)"""
        
    return dt_obj.strftime('%d%b%Y')




class SetupData():
    """
    Series of methods to return API data to the application. Call SetupData 
    class with boolean True/False to use the required DES proxy server.
    """
    
    def __init__(self, use_DES_proxy = False):
        if use_DES_proxy == True:
            self.proxy = DES_PROXY
        else:
            self.proxy = None
            
        self.default_start_date = datetime_obj_to_str(dt.datetime(2019, 1, 1))
        self.default_end_date = datetime_obj_to_str(dt.datetime.now()
                                                    +dt.timedelta(days = 1))
    
    def get_data_from_API(self, url, proxy = None):
        """
        Get data from the LondonAir API. If a connection cannot be made, print 
        a message to the console and exit.
        """
        
        try:
            response = requests.get(BASE_URL + url, proxies = proxy)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.ConnectionError:
            print("No response from LondonAir API server")
            exit(1) 
    
    
    def get_hourly_site_readings_between(self, site_code, 
                                         start_date = None, end_date = None):
        """
        Takes a site code, a start date, and an end date and recovers the hourly 
        particulate measurements between these two dates. Format for dates is 
        DDMonYYYY (01Jan2000); conversion of datetime objects can be done with 
        the datetime_obj_to_str() func.
        Returns a pandas Dataframe of the species measurements across the 
        datetime hours requested."""
        
        start_date = start_date if start_date is not None else self.default_start_date
        end_date = end_date if end_date is not None else self.default_end_date
        
        URL = ("/Data/Site/SiteCode="+str(site_code) +"/StartDate="+str(start_date)
                +"/EndDate="+str(end_date)+'/Json')
                        
        data = self.get_data_from_API(URL, self.proxy)
        if data is not None:
            hourly_data = data['AirQualityData']['Data']
            species = list(set([i['@SpeciesCode'] for i in hourly_data]))
            species_length = int(len(hourly_data) / len(species))
            
            spec_data = [hourly_data[spec*species_length:(spec*species_length)
                        +species_length] for spec in range(len(species))]
            
            hourly_df = pd.DataFrame(pd.Series(sorted(list(set(
                        [i['@MeasurementDateGMT'] for i in hourly_data])))))
            
            for spec in range(len(species)):
                values = [str(i['@Value']) for i in spec_data[spec]]
                hourly_df[species[spec]] = pd.Series(values)
                
            cols = list(hourly_df.columns)
            cols[0] = 'MeasurementDate'
            hourly_df.columns = cols
            return hourly_df.to_dict('records')
    
    
    def get_daily_index_latest(self, site_code):
        """
        Takes a site code, recovers the most current health index rating for that 
        site. 
        
        Returns a pandas DataFrame of the different species measured at that 
        site, includes the most current index, which band that falls under, the 
        index source, the species code, and the species name.
        """
        
        URL = "/Daily/MonitoringIndex/Latest/SiteCode="+str(site_code)+"/Json"
        data = self.get_data_from_API(URL, self.proxy)
        if data is not None:
            daily_index_latest = (data['DailyAirQualityIndex']['LocalAuthority']
                                    ["Site"]["Species"])
            
            keys = list(daily_index_latest[0].keys())
            daily_index_latest = [{k.strip('@') : species[k] for k in keys} 
                                    for species in daily_index_latest]
            return daily_index_latest
            
            
    
    def get_daily_index_on_date(self, site_code, date):
        """
        Takes a site code, and a date, and recovers the hourly 
        particulate measurements between these two dates. Format for dates is 
        DDMonYYYY (01Jan2000); conversion of datetime objects can be done with 
        the self.datetime_obj_to_str() func.
        
        Returns a pandas DataFrame of the different species measured at that 
        site, includes the most current index, which band that falls under, the 
        index source, the species code, and the species name.
        """
        
        if type(date) == dt.datetime:
            date = self.datetime_obj_to_str(date)
        URL = "/Daily/MonitoringIndex/SiteCode="+str(site_code)+"/Date="+str(date)+"/Json"
        data = self.get_data_from_API(URL, self.proxy)
        if data is not None:
            daily_index_dated = (data['DailyAirQualityIndex']['LocalAuthority']
                                ["Site"]["Species"])
            keys = list(daily_index_dated[0].keys())
            daily_index_dated = [{k.strip('@') : species[k] for k in keys} 
                                    for species in daily_index_dated]
            return daily_index_dated
            
    
    def nowcast(self, lat, long):
        """
        Takes a latitude and longitude, and interpolates between nearby measurement 
        sites. 
        
        Returns a dictionary with keys:
        ['@lat', '@lon', '@Easting', '@Northing', '@NO2_Annual', '@O3_Annual', 
        '@PM10_Annual', '@PM25_Annual', '@NO2', '@O3', '@PM10', '@PM25', 
        '@NO2_Index', '@O3_Index', '@PM10_Index', '@PM25_Index', '@Max_Index']
        """
        URL = "/Data/Nowcast/lat="+str(lat)+"/lon="+str(long)+"/Json"
        data = self.get_data_from_API(URL)
        if data is not None:
            return data['PointResult']

    

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
            {"lat":-37.90295525,"lng":175.4772238333,"carbon-monoxide":0.331566754675031,"nitrogen-dioxide":1},
            {"lat":-37.9155634,"lng":175.47150915,"carbon-monoxide":0.0553410958886463,"nitrogen-dioxide":1},
            {"lat":-37.9077980667,"lng":175.4749606833,"carbon-monoxide":0.0892525576065953,"nitrogen-dioxide":1},
            {"lat":-37.9024718333,"lng":175.47689145,"carbon-monoxide":0.590075732442714,"nitrogen-dioxide":1},
            {"lat":-37.9010265333,"lng":175.4781286667,"carbon-monoxide":0.15434154031539,"nitrogen-dioxide":1},
            {"lat":-37.9051546167,"lng":175.4761810167,"carbon-monoxide":0.545913378087492,"nitrogen-dioxide":1},
            {"lat":-37.9027743667,"lng":175.4772973,"carbon-monoxide":0.633489041919876,"nitrogen-dioxide":1},
            {"lat":-37.9113692333,"lng":175.4732625,"carbon-monoxide":0.266503161072438,"nitrogen-dioxide":1},
            {"lat":-37.9061175,"lng":175.4761095667,"carbon-monoxide":0.276762853991245,"nitrogen-dioxide":1},
            {"lat":-37.9126536833,"lng":175.4718492,"carbon-monoxide":0.1891805552013,"nitrogen-dioxide":1},
            {"lat":-37.89984655,"lng":175.47884775,"carbon-monoxide":0.0675455473384583,"nitrogen-dioxide":1},
            {"lat":-37.8996625,"lng":175.4783593833,"carbon-monoxide":0.0330886810539454,"nitrogen-dioxide":1},
            {"lat":-37.9096838,"lng":175.4734820333,"carbon-monoxide":0.555126115173718,"nitrogen-dioxide":1},
            {"lat":-37.9163971333,"lng":175.4703382333,"carbon-monoxide":0.825905559386503,"nitrogen-dioxide":1},
            {"lat":-37.9019659333,"lng":175.47801565,"carbon-monoxide":0.96350573450757,"nitrogen-dioxide":1},
            {"lat":-37.9017677,"lng":175.4778972667,"carbon-monoxide":0.655546251121835,"nitrogen-dioxide":1},
            {"lat":-37.9082934833,"lng":175.4747193,"carbon-monoxide":0.668460695656423,"nitrogen-dioxide":1},
            {"lat":-37.9124935167,"lng":175.4721662833,"carbon-monoxide":0.62742638749223,"nitrogen-dioxide":1},
            {"lat":-37.9112822667,"lng":175.4727057,"carbon-monoxide":0.488621588652691,"nitrogen-dioxide":1},
            {"lat":-37.9088314833,"lng":175.4744561333,"carbon-monoxide":0.761584090132723,"nitrogen-dioxide":1},
            {"lat":-37.9140193667,"lng":175.4723065,"carbon-monoxide":0.893369510759159,"nitrogen-dioxide":1},
            {"lat":-37.9151048833,"lng":175.4715047667,"carbon-monoxide":0.330237470617188,"nitrogen-dioxide":1},
            {"lat":-37.9155721667,"lng":175.4712705333,"carbon-monoxide":0.846069812688032,"nitrogen-dioxide":1},
            {"lat":-37.91564375,"lng":175.4698925833,"carbon-monoxide":0.382826719439399,"nitrogen-dioxide":1},
            {"lat":-37.9157315333,"lng":175.4712060333,"carbon-monoxide":0.0212573374476552,"nitrogen-dioxide":1},
            {"lat":-37.9158956833,"lng":175.4711298667,"carbon-monoxide":0.495373866646281,"nitrogen-dioxide":1},
            {"lat":-37.9044821667,"lng":175.4765082167,"carbon-monoxide":0.802100320556479,"nitrogen-dioxide":1},
            {"lat":-37.9045073333,"lng":175.4759204333,"carbon-monoxide":0.766882008309998,"nitrogen-dioxide":1},
            {"lat":-37.9046759167,"lng":175.4758561667,"carbon-monoxide":0.970506803458753,"nitrogen-dioxide":1},
            {"lat":-37.8983034667,"lng":175.4792230333,"carbon-monoxide":0.17487089909492,"nitrogen-dioxide":1},
            {"lat":-37.8987899833,"lng":175.4796567167,"carbon-monoxide":0.560477608746508,"nitrogen-dioxide":1}
        ]

def main():
    setup = SetupData(use_DES_proxy = False)
    a = setup.nowcast('51.563752', '0.177891')    
    return a
    
if __name__ == "__main__":
    a = main()
    