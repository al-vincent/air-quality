from django.test import TestCase, Client

from Emissions.views import index
from Emissions.models import Species

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