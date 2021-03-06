from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from .base import FunctionalTest


class NewVisitorTest(FunctionalTest):
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

    def test_entering_second_person(self):
        self.browser.get(self.live_server_url)
        inputbox = self.get_item_input_box()
        self.assertEqual(
            inputbox.get_attribute("placeholder"),
            "Enter a To-Do item"
        )
        # Try entering someting
        inputbox.send_keys("Buy some chocolate")
        inputbox.send_keys(Keys.ENTER)
        milkas_list_url = self.browser.current_url
        self.assertRegex(milkas_list_url, "/lists/.+")
        self.check_for_row_in_list_table("1: Buy some chocolate")

        inputbox = self.get_item_input_box()
        inputbox.send_keys("Eat the chocolate")
        inputbox.send_keys(Keys.ENTER)
        self.check_for_row_in_list_table("2: Eat the chocolate")

        self.browser.quit()
        self.browser = webdriver.Firefox()
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element_by_tag_name("body").text
        self.assertNotIn("Buy some chocolate", page_text)
        self.assertNotIn("Eat the chocolate", page_text)

        inputbox = self.get_item_input_box()
        inputbox.send_keys("Buy milk")
        inputbox.send_keys(Keys.ENTER)

        emmas_list_url = self.browser.current_url
        self.assertRegex(emmas_list_url, "/lists/.+")
        self.assertNotEqual(emmas_list_url, milkas_list_url)

        page_text = self.browser.find_element_by_tag_name("body").text
        self.assertNotIn("Buy some chocolate", page_text)
        self.assertIn("Buy milk", page_text)
