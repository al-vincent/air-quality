from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import time
import platform
from Emissions.models import Species, LocalAuthority, Site

class NewVisitorTest(StaticLiveServerTestCase):
    def setUp(self):
        Species.objects.create(name="Carbon Monoxide", code="CO")
        Species.objects.create(name="Nitrogen Dioxide", code="NO2")

        if platform.system() == "Windows":
            self.browser = webdriver.Chrome()
        else:
            from selenium.webdriver.firefox.options import Options
            options = Options()
            options.add_argument('-headless')
            self.browser = webdriver.Firefox(firefox_options=options)
        
        self.browser.implicitly_wait(5)
        # Cornelius opens the homepage
        self.browser.get(self.live_server_url)
    
    def tearDown(self):
        self.browser.quit()
    
    def test_open_page(self):        
        # He sees that the page's title includes the phrase "Air Quality"
        self.assertIn("Air Quality", self.browser.title)
    
    # def test_map_exists(self):
        # He is presented with a map of the London area
        emissions_map = self.browser.find_element_by_id("map")
        # Check that the map element has the class "leaflet-container"
        self.assertIn("leaflet-container", emissions_map.get_attribute("class"))

    # def test_emissions_menu_items(self):
        # He sees a drop-down menu to choose an emissions type to view. There is 
        # a default value, of carbon monoxide
        emissions_menu = self.browser.find_element_by_id("list-emissions")
        # check that the element is a select element (i.e. drop-down)
        Select(emissions_menu) 
        # get the first option in the list
        option = emissions_menu.find_element_by_tag_name("option")
        # test for both the 'value' attribute and the 'text' attribute
        # (not required, but useful syntax!)
        self.assertEqual( option.get_attribute("value"), "CO" )
        self.assertEqual( option.get_attribute("text"), "Carbon Monoxide" )       

    # def test_local_auths_menu_items(self):
        # Cornelius sees a drop-down for selecting an area of London. The default value
        # is "All Local Authorities"
        geographic_menu = self.browser.find_element_by_id("list-london-areas")
        # check that the element is a select element
        Select(geographic_menu)
        # get the first option in the list
        option = geographic_menu.find_element_by_tag_name("option")
        self.assertEqual( option.get_attribute("value"), "0" )
        self.assertEqual( option.text, "All Local Authorities" )

    # def test_emissions_info_population(self):
        # Information about the emissions type is shown further down again.
        emissions_title = self.browser.find_element_by_id("title-emissions")
        self.assertEqual(emissions_title.text, "Nitrogen Dioxide")
    
    # def change_default_values(self):
        # # Cornelius opens the homepage
        # self.browser.get(self.live_server_url)

        # he sees a map and three drop-down menus
        emissions_map = self.browser.find_element_by_id("map")
        emissions_menu = self.browser.find_element_by_id("list-emissions")
        geographic_menu = self.browser.find_element_by_id("list-london-areas")

        # Cornelius changes the value in the emissions drop-down to nitrogen dioxide, 
        # and the map updates to show the new values        
        emissions_menu.send_keys("Nitrogen Dioxide")
        time.sleep(1) # pauses the page for a second (useful to view the change)

        # He selects "barnet" from the drop-down
        geographic_menu.send_keys("Barnet")
        time.sleep(1)   

        # The map re-renders to show this area, at a zoom level of <...??...>
        pass
