from django.test import TestCase
from django.urls import resolve
from Emissions.views import index


class HomePageTest(TestCase):
    
    def root_url_resolves_to_home_page(self):
        # this will find the function that maps to the "/" route
        found = resolve("/")
        # this tests whether the function for "/" is the 'imdex' function
        # (I assert it should be)
        self.assertEqual(found.func, index)
    
    def runTest(self):
        self.root_url_resolves_to_home_page()