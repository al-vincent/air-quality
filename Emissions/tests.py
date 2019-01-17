from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest

from Emissions.views import index


class HomePageTest(TestCase):

    def index_returns_correct_html(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "index.html")

    def runTest(self):
        self.index_returns_correct_html()