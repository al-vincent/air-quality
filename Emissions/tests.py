from django.test import TestCase, Client

from Emissions.views import index
from Emissions.models import Species
from Emissions.services import AirQualityApiData

class ServicesTest(TestCase):
    # Add tests for the following:
    # - datetime_obj_to_string
    #     -- try a few correct examples, check returns
    #     -- try a few incorrect examples; handling?
    #     -- what's the date range? Should we set a global min (e.g. date when 
    #        data collection first started)?

    
    # - AirQualityApiData()
    #     -- does the constructor work properly? Test with arg=True, False, None
    
    #     -- get_hourly_site_readings; test with correct API against sample data;
    #     site code not supplied; start_date not supplied; end_date not supplied; 
    #     whether the pivot behaves as expected; do columns rename correctly;
    #     whether no data from API returns None from the function
    #     -- get_daily_index_on_date...
    def setUp(self):
        self.api = AirQualityApiData(use_DES_proxy=False)
    
    def tearDown(self):
        del self.api

    # ------------------------------------------------------------------------------------
    # Test get_current_emissions_across_london
    # ------------------------------------------------------------------------------------
    #   test with valid API and sample data, no URL, incorrect stem URL
    #
    #   Notes; 
    #     - case where URLs are valid, but pointing to an XML or CSV source 
    #       is not currently handled?
    #     - need to test proxy (requires DES, or other network with a proxy)
    def test_get_data_from_API_valid_API(self):
        # test with valid API (whose output doesn't change over time)
        test_url = "/Information/Species/SpeciesCode=CO/Json"
        correct_return = {"AirQualitySpecies": 
                            {"Species": 
                                {"@SpeciesCode":"CO",
                                "@SpeciesName":"Carbon Monoxide",
                                "@Description":"Carbon Monoxide is a colourless, odourless poisonous gas produced by incomplete, or inefficient, combustion of fuel including 'cold' or badly tuned engines.","@HealthEffect":"The gas affects the transport of oxygen around the body by the blood. At very high levels, this can lead to a significant reduction in the supply of oxygen to the heart, particularly in people suffering from heart disease.",
                                "@Link":"http://www.londonair.org.uk/LondonAir/guide/WhatIsCO.aspx"
                                }
                            }
                        }
        test_return = self.api.get_data_from_API(url=test_url)
        self.assertEqual(test_return, correct_return)
    
    def test_get_data_from_API_invalid_API(self):
        test_url = "sldfkns"    # arbitrary, nonexistent API end-point
        correct_return = None
        test_return = self.api.get_data_from_API(url=test_url)
        self.assertEqual(test_return, correct_return)

    def test_get_data_from_API_empty_url(self):
        test_url = ""    
        correct_return = None
        test_return = self.api.get_data_from_API(url=test_url)
        self.assertEqual(test_return, correct_return)
    
    # ------------------------------------------------------------------------------------
    # Test setup_row_dict
    # ------------------------------------------------------------------------------------
    #   test with valid site_data (i.e. all fields populated); poorly-formed site_data;
    #   valid la_data, no la_data
    # 
    #   Notes; 
    #     - better to spec the functions with required types in the header, using '=>' ?
    def test_setup_row_dict_valid_data(self):
        la_name = "My local auth"
        site_data = {"@SiteName": "name of site",
                     "@SiteCode": "code of site",
                     "@SiteType": "type of site",
                     "@BulletinDate": "01-01-2019",
                     "@Latitude": "1.23456",
                     "@Longitude": "9.87654"}
        correct_return = {"Local Authority name": "My local auth", 
                        "Site name": "name of site",
                        "Site code": "code of site", 
                        "Site type": "type of site", 
                        "Date": "01-01-2019", 
                        "Latitude": 1.23456, 
                        "Longitude": 9.87654, 
                        "Carbon Monoxide": None, 
                        "Nitrogen Dioxide": None, 
                        "Sulphur Dioxide": None, 
                        "Ozone": None, 
                        "PM10 Particulate": None, 
                        "PM2.5 Particulate": None}
        test_return = self.api.setup_row_dict(site_data=site_data, la_name=la_name)
        self.assertEqual(test_return, correct_return)

    def test_setup_row_dict_invalid_site_data(self):
        la_name = "My local auth"
        site_data = {"@SiteName": "name of site",
                     "@SiteType": "type of site",
                     "@BulletinDate": "01-01-2019",
                     "@Latitude": "1.23456",
                     "@Longitude": "9.87654"}
        correct_return = None
        test_return = self.api.setup_row_dict(site_data=site_data, la_name=la_name)
        self.assertEqual(test_return, correct_return)

    # ------------------------------------------------------------------------------------
    # Test get_current_emissions_across_london
    # ------------------------------------------------------------------------------------
    # Test cases:
    #   - 'Standard', fairly well-formatted json; 'Site' is a list, 'Species' is a list
    #   - 'Site' component of json is a dict
    #   - 'Species' component of json is a dict
    #   - Neither 'Site' nor 'Species' are a list *or* a dict
    #   - No return from API
    #   - 400 error from API

class HomePageTest(TestCase):

    def setUp(self):
        emission1 = Species.objects.create(name="Carbon Monoxide")
        emission2 = Species.objects.create(name="Nitrogen Dioxide")

    def test_emissions_count(self):
        saved_emissions = Species.objects.all()
        self.assertEqual(saved_emissions.count(), 2)

    def test_index_returns_correct_html(self):
        # create a Client object and use it to get a response from the home page
        c = Client()
        response = c.get("/")
        # test that the response is valid
        self.assertEqual(response.status_code, 200)
        # test that the homepage is using the index.html template
        self.assertTemplateUsed(response, "Emissions/index.html")

    def test_retrieving_emissions_from_db(self):
        saved_emissions = Species.objects.all()
        first_saved_emission = saved_emissions[0]
        second_saved_emission = saved_emissions[1]
        self.assertEqual(first_saved_emission.name, "Carbon Monoxide")
        self.assertEqual(second_saved_emission.name, "Nitrogen Dioxide")
