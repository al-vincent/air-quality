from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from Emissions.models import Species, LocalAuthority, Site
from django.conf import settings

import time
import os
from json import load

# -----------------------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------------------
def get_webdriver():
    if 'BUILD_ENV' in os.environ:
        from selenium.webdriver.firefox.options import Options
        options = Options()
        options.add_argument('-headless')
        return webdriver.Firefox(firefox_options=options)
    else:
        return webdriver.Chrome()

# -----------------------------------------------------------------------------------------
# TEST CLASSES
# -----------------------------------------------------------------------------------------
class LoadPageTests(StaticLiveServerTestCase):
    # read in config vars
    with open(os.path.join(settings.STATIC, 'js/config.json'), "r") as f:
        CONFIG = load(f)["HTML"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()                
        # set up the webdriver
        cls.browser = get_webdriver()
        cls.browser.implicitly_wait(3)
    
    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()
    
    def setUp(self):
        # Cornelius opens the homepage
        self.browser.get(self.live_server_url)
    
    def test_page_has_correct_title(self):        
        # He sees that the page's title includes the phrase "Air Quality"
        self.assertIn("Air Quality", self.browser.title)

    def test_emissions_menu_is_visible(self):
        # He sees a drop-down menu to choose an emissions type to view. 
        emissions_menu = self.browser.find_element_by_id(self.CONFIG["LISTS"]["EMISSION_LIST_ID"])
        self.assertTrue(emissions_menu.is_displayed())
        # check that the element is a select element (i.e. drop-down)
        select = Select(emissions_menu)
        # check that the list is empty (it should be, initially)
        self.assertAlmostEqual(len(select.options), 0)
        
    def test_local_auths_menu_is_visible(self):
        # Cornelius sees a drop-down for selecting an area of London. The default value
        # is "All Local Authorities"
        local_auths_menu = self.browser.find_element_by_id(self.CONFIG["LISTS"]["LOCAL_AUTHS_LIST_ID"])
        # check that the element is a select element
        select = Select(local_auths_menu)
        # check that the list contains one element
        self.assertAlmostEqual(len(select.options), 1)
    
    def test_map_is_visible(self):
        # He is presented with a map of the London area
        emissions_map = self.browser.find_element_by_id(self.CONFIG["MAP"]["ID"])
        self.assertTrue(emissions_map.is_displayed())
        # Check that the map element has the class "leaflet-container"
        # self.assertIn(self.CONFIG["MAP"]["CLASS"], emissions_map.get_attribute("class"))

    def test_emissions_title_visible_correct_defaults(self):
        TITLE = self.CONFIG["EMISSIONS"]["TITLE"]
        # A panel is shown with information about the emissions type
        # It contains an overall title element
        emissions_title = self.browser.find_element_by_id(TITLE["ID"])
        self.assertTrue(emissions_title.is_displayed())
        # Check the default text of the title
        self.assertEqual(emissions_title.text, TITLE["TEXT"])

    def test_emissions_description_visible_correct_defaults(self):
        # The panel also contains a text description of the emission, with subtitle 
        # and body-text elements
        DESC = self.CONFIG["EMISSIONS"]["DESCRIPTION"] 
        # check the subtitle element is visible
        description_subtitle = self.browser.find_element_by_id(DESC["TITLE"]["ID"])
        self.assertTrue(description_subtitle.is_displayed())
        # Check the default text of the subtitle
        self.assertEqual(description_subtitle.text, DESC["TITLE"]["TEXT"])

        # check the body text element is visible
        description_bodytext = self.browser.find_element_by_id(DESC["BODY"]["ID"])
        self.assertTrue(description_bodytext.is_displayed())
        # Check the default text of the subtitle
        self.assertEqual(description_bodytext.text, DESC["BODY"]["TEXT"])

    def test_emissions_health_effects_visible_correct_defaults(self):
        # Finally, the panel contains info on the health impacts of the emission, with 
        # subtitle and body-text elements
        HEALTH = self.CONFIG["EMISSIONS"]["HEALTH_EFFECTS"] 
        # check the subtitle element is visible
        health_subtitle = self.browser.find_element_by_id(HEALTH["TITLE"]["ID"])
        self.assertTrue(health_subtitle.is_displayed())
        # Check the default text of the subtitle
        self.assertEqual(health_subtitle.text, HEALTH["TITLE"]["TEXT"])

        # check the body text element is visible
        health_bodytext = self.browser.find_element_by_id(HEALTH["BODY"]["ID"])
        self.assertTrue(health_bodytext.is_displayed())
        # Check the default text of the subtitle
        self.assertEqual(health_bodytext.text, HEALTH["BODY"]["TEXT"])

    def test_local_auths_panel_is_invisible(self):
        local_auths = self.browser.find_element_by_id(self.CONFIG["LOCAL_AUTHS"]["CONTAINER_ID"])
        self.assertFalse(local_auths.is_displayed())        
    
    def test_about_panel_is_visible_correct_defaults(self):
        ABOUT = self.CONFIG["ABOUT"]
        # check the panel is visible
        about_title = self.browser.find_element_by_id(ABOUT["TITLE"]["ID"])
        self.assertTrue(about_title.is_displayed())
        # check that the title text is correct
        self.assertEqual(about_title.text, ABOUT["TITLE"]["TEXT"])

    # def test_emissions_info_population(self):
    #     # Information about the emissions type is shown further down again.
    #     emissions_title = self.browser.find_element_by_id("title-emissions")
    #     self.assertEqual(emissions_title.text, "Nitrogen Dioxide")

    # def test_change_default_values(self):
    #     # # Cornelius opens the homepage
    #     # self.browser.get(self.live_server_url)

    #     # he sees a map and three drop-down menus
    #     emissions_map = self.browser.find_element_by_id("map")
    #     emissions_menu = self.browser.find_element_by_id("list-emissions")
    #     geographic_menu = self.browser.find_element_by_id("list-london-areas")

    #     # Cornelius changes the value in the emissions drop-down to nitrogen dioxide, 
    #     # and the map updates to show the new values        
    #     emissions_menu.send_keys("Nitrogen Dioxide")
    #     time.sleep(1) # pauses the page for a second (useful to view the change)

    #     # He selects "barnet" from the drop-down
    #     geographic_menu.send_keys("Barnet")
    #     time.sleep(1)   

    #     # The map re-renders to show this area, at a zoom level of <...??...>
    #     pass

# class MapTests(StaticLiveServerTestCase):
#     def setUp(self):
#         # read in config vars
#         with open(os.path.join(settings.STATIC, 'js/config.json'), "r") as f:
#             self.CONFIG = load(f)["HTML"]
        
#         # set up the webdriver
#         self.browser = get_webdriver()
#         self.browser.implicitly_wait(3)
        
#         # Cornelius opens the homepage
#         self.browser.get(self.live_server_url)
    
#     def tearDown(self):
#         self.browser.quit()

# class EmissionsMenuTests(StaticLiveServerTestCase):
#     def setUp(self):
#         # read in config vars
#         with open(os.path.join(settings.STATIC, 'js/config.json'), "r") as f:
#             self.CONFIG = load(f)["HTML"]
        
#         # set up the webdriver
#         self.browser = get_webdriver()
#         self.browser.implicitly_wait(3)
        
#         # Cornelius opens the homepage
#         self.browser.get(self.live_server_url)

#         # Create two test Species        
#         Species.objects.create(name="Carbon Monoxide", code="CO")
#         Species.objects.create(name="Nitrogen Dioxide", code="NO2")
    
#     def tearDown(self):
#         self.browser.quit()

#     def test_default_settings(self):
#         emissions_menu = self.browser.find_element_by_id(self.CONFIG["LISTS"]["EMISSION_LIST_ID"])
#         # There is a default value, of carbon monoxide
#         # get the first option in the list
#         option = emissions_menu.find_element_by_tag_name("option")
#         # test for both the 'value' attribute and the 'text' attribute
#         # (not required, but useful syntax!)
#         self.assertEqual( option.get_attribute("value"), "CO" )
#         self.assertEqual( option.get_attribute("text"), "Carbon Monoxide" ) 

# class LocalAuthorityMenuTests(StaticLiveServerTestCase):
#     def setUp(self):
#         # read in config vars
#         with open(os.path.join(settings.STATIC, 'js/config.json'), "r") as f:
#             self.CONFIG = load(f)["HTML"]
        
#         # set up the webdriver
#         self.browser = get_webdriver()
#         self.browser.implicitly_wait(3)
        
#         # Cornelius opens the homepage
#         self.browser.get(self.live_server_url)
    
#     def tearDown(self):
#         self.browser.quit()
    
#     def test_default_settings(self):
#         local_auths_menu = self.browser.find_element_by_id(self.CONFIG["LISTS"]["LOCAL_AUTHS_LIST_ID"])
#         # get the first option in the list
#         option = local_auths_menu.find_element_by_tag_name("option")
#         self.assertEqual( option.get_attribute("value"), "0" )
#         self.assertEqual( option.text, "All Local Authorities" )

# class SiteControlTests(StaticLiveServerTestCase):
#     def setUp(self):
#         # read in config vars
#         with open(os.path.join(settings.STATIC, 'js/config.json'), "r") as f:
#             self.CONFIG = load(f)["HTML"]
        
#         # set up the webdriver
#         self.browser = get_webdriver()
#         self.browser.implicitly_wait(3)
        
#         # Cornelius opens the homepage
#         self.browser.get(self.live_server_url)
    
#     def tearDown(self):
#         self.browser.quit()
