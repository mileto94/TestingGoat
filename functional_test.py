from selenium import webdriver
import unittest


class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_with_wrong_title(self):
        self.browser.get("http://localhost:8000")
        self.assertIn("To do", self.browser.title)
        self.fail("Finish the test")

if __name__ == '__main__':
    unittest.main(warnings="ignore")


# This is the test without using unittest library
# browser = webdriver.Firefox()
# browser.get('http://localhost:8000')

# assert 'To do' in browser.title, "Browser title was" + browser.title

# browser.quit()
