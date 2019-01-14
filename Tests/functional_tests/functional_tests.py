from selenium import webdriver
import unittest

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
        # User opens the homepage
        self.browser.get("http://localhost:8000")

        # user sees that the page's title includes the phrase "Air Quality"
        self.assertIn("Air Quality", self.browser.title)
        # add a test fail, to remind us to finish the tests
        self.fail("Finish the test")

        # user sees a map of the London area

        # user sees a selection box to choose an emissions type on the RHS

        # user sees a search box on the RHS

        # user sees a selection box that shows different types of illness on the RHS     

if __name__ == "__main__":
    unittest.main(warnings="ignore")
