from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
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
    
    def open_page_test(self):
        # Cornelius opens the homepage
        self.browser.get("http://localhost:8000")

        # He sees that the page's title includes the phrase "Air Quality"
        self.assertIn("Air Quality", self.browser.title)
    
        # He is presented with a map of the London area
        emissions_map = self.browser.find_element_by_id("map")
        # NOTE: need more than this. Can I test if a Leaflet map is actually displayed?
        # E.g. check against the class? [I assume Leaflet maps have a particular class]
        self.assertIn("leaflet-container", emissions_map.get_attribute("class"))

        # He sees a drop-down menu to choose an emissions type to view. There is 
        # a default value, of carbon monoxide
        emissions_menu = self.browser.find_element_by_id("list-emissions")
        # check that the element is a select element (i.e. drop-down)
        Select(emissions_menu) 
        # get the first option in the list
        option = emissions_menu.find_element_by_tag_name("option")
        # test for both the 'value' attribute and the 'text' attribute
        # (not required, but useful syntax!)
        self.assertEqual( option.get_attribute("value"), "carbon-monoxide" )
        self.assertEqual( option.get_attribute("text"), "Carbon Monoxide" )       

        # Cornelius sees a drop-down for selecting an area of London. The default value
        # is "All"
        geographic_menu = self.browser.find_element_by_id("list-london-areas")
        # check that the element is a select element
        Select(geographic_menu)
        # get the first option in the list
        option = geographic_menu.find_element_by_tag_name("option")
        self.assertEqual( option.get_attribute("value"), "all" )
        self.assertEqual( option.text, "All" )

        # Cornelius sees a selection box that shows different types of illness. 
        # The default value is <...??...>.  
        illness_menu = self.browser.find_element_by_id("list-illnesses")
        # check that the element is a select element
        Select(illness_menu)
        # get the first option in the list
        option = illness_menu.find_element_by_tag_name("option")
        self.assertEqual( option.get_attribute("value"), "asthma" )
        self.assertEqual( option.text, "Asthma" )
        
        # Information about this illness is shown further down the page.
        illness_info = self.browser.find_element_by_id("info-illness")
        self.assertEqual(
            illness_info.text, "Info about the default illness"
        )               
    
    def change_default_values(self):
        # Cornelius opens the homepage
        self.browser.get("http://localhost:8000")

        # he sees a map and three drop-down menus
        emissions_map = self.browser.find_element_by_id("map")
        emissions_menu = self.browser.find_element_by_id("list-emissions")
        geographic_menu = self.browser.find_element_by_id("list-london-areas")
        illness_menu = self.browser.find_element_by_id("list-illnesses")

        # Cornelius changes the value in the emissions drop-down to nitrogen dioxide, 
        # and the map updates to show the new values        
        emissions_menu.send_keys("Nitrogen Dioxide")
        time.sleep(1) # pauses the page for a second (useful to view the change)

        # He types in "barnet"        
        geographic_menu.send_keys("Barnet")
        time.sleep(1)   

        # The map re-renders to show this area, at a zoom level of <...??...>

        # He changes the illness to <...??...>, and the information updates.
        illness_menu.send_keys("Emphesema")
        time.sleep(1)
        # illness_info = self.browser.find_element_by_id("info-illness")
        # self.assertEqual(
        #     illness_info.get_attribute("...??..."), "Info about the updated illness"
        # )
        pass
    
    def runTest(self):
        self.open_page_test()
        self.change_default_values()
        
        # add a test fail, to remind us to finish the tests
        self.fail("Finish the test")

if __name__ == "__main__":
    unittest.main(warnings="ignore")
