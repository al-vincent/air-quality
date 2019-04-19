from django.test import TestCase, Client

from Emissions.views import index
from Emissions.models import Species
from Emissions.services import AirQualityApiData

class ServicesTest(TestCase):
    pass
    # Add tests for the following:
    # - datetime_obj_to_string
    #     -- try a few correct examples, check returns
    #     -- try a few incorrect examples; handling?
    #     -- what's the date range? Should we set a global min (e.g. date when 
    #        data collection first started)?
    # - SetupPage()
    #     -- does the constructor work properly? Test with arg=True, False, None
    #     -- get_data_from_API; test with actual API and sample data, no URL,
    #     incorrect root URL, incorrect stem URL [Note; case where URLs are valid,
    #     but pointing to an XML or CSV source is not currently handled?]
    #     -- get_hourly_site_readings; test with correct API against sample data;
    #     site code not supplied; start_date not supplied; end_date not supplied; 
    #     whether the pivot behaves as expected; do columns rename correctly;
    #     whether no data from API returns None from the function
    #     -- get_daily_index_on_date...

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