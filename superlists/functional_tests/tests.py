from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.test import LiveServerTestCase


class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def check_for_row_in_list_table(self, row_text):
        table = self.browser.find_element_by_id("id_list_table")
        rows = table.find_elements_by_tag_name("tr")
        self.assertIn(row_text, [row.text for row in rows])

    def test_with_wrong_title(self):
        self.browser.get(self.live_server_url)

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
        self.check_for_row_in_list_table("1: Buy some chocolate")

        inputbox = self.browser.find_element_by_id("id_new_item")
        inputbox.send_keys("Eat the chocolate")
        inputbox.send_keys(Keys.ENTER)
        self.check_for_row_in_list_table("2: Eat the chocolate")

        self.fail("Finish the test")