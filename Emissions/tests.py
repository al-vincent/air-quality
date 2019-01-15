from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest

from Emissions.views import index


class HomePageTest(TestCase):
    
    def root_url_resolves_to_index_view(self):
        # this will find the function that maps to the "/" route
        found = resolve("/")
        # this tests whether the function for "/" is the 'imdex' function
        # (I assert it should be)
        self.assertEqual(found.func, index)
    
    def index_returns_correct_html(self):
        request = HttpRequest()
        response = index(request)
        html = response.content.decode("utf8")
        self.assertTrue(html.startswith("<html>"))
        self.assertIn("<title>Air Quality</title>", html)
        self.assertTrue(html.endswith("</html>"))

    def runTest(self):
        self.root_url_resolves_to_index_view()
        self.index_returns_correct_html()