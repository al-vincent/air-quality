from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest
import time

class NewVisitorTest(unittest.TestCase):
    
    # NOTE: setUp and tearDown are special unittest built-ins; DON'T try to
    # use different naming conventions, or they won't do what they're supposed 
    # to! [setUp runs before any tests, tearDown runs once all tests are 
    # complete]

    def setUp(self):
        print("Browser opened")
        self.browser = webdriver.Chrome()
    
    def tearDown(self):
        self.browser.quit()
    
    def test_open_page(self):
        # Cornelius opens the homepage
        self.browser.get("http://localhost:8000")

        # He sees that the page's title includes the phrase "Air Quality"
        self.assertIn("Air Quality", self.browser.title)
    
        # He is presented with a map of the London area
        map = self.browser.find_element_by_id("map")
        # NOTE: need more than this. Can I test if a Leaflet map is actually displayed?
        # E.g. check against the class? [I assume Leaflet maps have a particular class]
        self.assertEqual(map.__class__, "leaflet-container")

        # He sees a drop-down menu to choose an emissions type to view. There is 
        # a default value, of carbon monoxide
        emissions_menu = self.browser.find_element_by_id("list-emissions")
        self.assertEqual(
            emissions_menu.get_attribute("value"), "carbon monoxide"
        )

        # He changes this to nitrogen dioxide, and the map updates to show the 
        # new values
        emissions_menu.send_keys("Nitrogen Dioxide")

        # Cornelius sees a search box [? or drop-down?] for selecting an area of London. 
        # He types in "Croydon"
        geographic_menu = self.browser.find_element_by_id("list-london-areas")
        geographic_menu.send_keys("Croydon")
        time.sleep(1)   # the page will refresh; this 'enforced wait' allows it to render

        # The map re-renders to show this area, at a zoom level of <...??...>

        # Cornelius sees a selection box that shows different types of illness. 
        # The default value is <...??...>.  
        illness_menu = self.browser.find_element_by_id("list-illnesses")
        self.assertEqual(
            illness_menu.get_attribute("Asthma"), "Asthma"
        )

        # Information about this illness is shown further down the page.
        illness_info = self.browser.find_element_by_id("info-illness")
        self.assertEqual(
            illness_info.get_attribute("...??..."), "Info about the default illness"
        )

        # He changes the illness to <...??...>, and the information updates.
        illness_menu.send_keys("Emphesema")
        time.sleep(1)
        illness_info = self.browser.find_element_by_id("info-illness")
        self.assertEqual(
            illness_info.get_attribute("...??..."), "Info about the updated illness"
        )

        # add a test fail, to remind us to finish the tests
        self.fail("Finish the test")

if __name__ == "__main__":
    unittest.main(warnings="ignore")
