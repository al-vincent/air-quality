from django.test import TestCase

from Emissions.views import index
from Emissions.models import Species

class HomePageTest(TestCase):

    def index_returns_correct_html(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "index.html")

    def retrieving_emissions_from_db(self):
        emission1 = Species()
        emission1.name = "Carbon Monoxide"
        emission1.save()

        emission2 = Species()
        emission2.name = "Nitrogen Dioxide"
        emission2.save()

        saved_emissions = Species.objects.all()
        self.assertEqual(saved_emissions.count(), 2)

        first_saved_emission = saved_emissions[0]
        second_saved_emission = saved_emissions[1]
        self.assertEqual(first_saved_emission.name, "Carbon Monoxide")
        self.assertEqual(second_saved_emission.name, "Nitrogen Dioxide")

    def runTest(self):
        self.index_returns_correct_html()
        self.retrieving_emissions_from_db()