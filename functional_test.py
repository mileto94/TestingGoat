from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest


class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_with_wrong_title(self):
        self.browser.get("http://localhost:8000")

        header_text = self.browser.find_element_by_tag_name("h1").text
        self.assertIn("To-Do", self.browser.title)
        self.assertIn("To-Do", header_text)

        inputbox = self.browser.find_element_by_id("id_new_item")
        self.assertEqual(
            inputbox.get_attribute("placeholder"),
            "Enter a to-do item"
        )

        # Try entering someting
        inputbox.send_keys("Buy some chocolate")

        inputbox.send_keys(Keys.ENTER)

        table = self.browser.find_element_by_id("id_list_table")
        rows = self.browser.find_elements_by_tag_name("tr")
        self.assertTrue(
            any(row.text == "1: Buy some chocolate" for row in rows),
            "New to-do item did not appear in table"
        )

        self.fail("Finish the test")

if __name__ == '__main__':
    unittest.main(warnings="ignore")


# This is the test without using unittest library
# browser = webdriver.Firefox()
# browser.get('http://localhost:8000')

# assert 'To do' in browser.title, "Browser title was" + browser.title

# browser.quit()
