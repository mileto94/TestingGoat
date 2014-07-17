from django.test import TestCase
from lists.models import Item, List
from django.utils.html import escape
from lists.forms import (EMPTY_LIST_ERROR, ItemForm,
            DUPLICATE_ITEM_ERROR, ExistingListItemForm)


class HomePageTest(TestCase):
    def test_hoem_page_renders_home_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")

    def test_home_page_uses_item_form(self):
        response = self.client.get("/")
        self.assertIsInstance(response.context["form"], ItemForm)


class ListViewTest(TestCase):
    def post_invalid_input(self):
        list_ = List.objects.create()
        return self.client.post(
            "/lists/%d/" % (list_.id),
            data={"text": ""}
        )

    def test_invalid_input_not_saved_to_db(self):
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_list_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "list.html")

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_LIST_ERROR))

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get("/lists/%d/" % (list_.id,))
        self.assertTemplateUsed(response, "list.html")

    def test_displays_only_items_for_that_list(self):
        correct_list = List.objects.create()
        Item.objects.create(text="item 1", list=correct_list)
        Item.objects.create(text="item 2", list=correct_list)

        other_list = List.objects.create()
        Item.objects.create(text="other list item 1", list=other_list)
        Item.objects.create(text="other list item 2", list=other_list)

        response = self.client.get("/lists/%d/" % (correct_list.id))

        self.assertContains(response, "item 1")
        self.assertContains(response, "item 2")
        self.assertNotContains(response, "other list item 1")
        self.assertNotContains(response, "other list item 2")

    def test_passes_correct_list_to_template(self):
        correct_list = List.objects.create()
        # other_list = List.objects.create()

        response = self.client.get("/lists/%d/" % (correct_list.id))

        self.assertEqual(response.context["list"], correct_list)

    def test_saving_a_POST_request(self):
        correct_list = List.objects.create()
        # other_list = List.objects.create()

        self.client.post(
            "/lists/%d/" % (correct_list.id,),
            data={"text": "A new item for an excisting list"}
        )
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new item for an excisting list")
        self.assertEqual(new_item.list, correct_list)

    def test_invalid_items_arent_saved(self):
        self.client.post("/lists/new", data={"text": ""})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

    def test_displays_item_form(self):
        list_ = List.objects.create()
        response = self.client.get("/lists/%d/" % (list_.id))
        self.assertIsInstance(response.context["form"], ExistingListItemForm)
        self.assertContains(response, 'name="text"')

    def test_form_save_handles_saving_to_a_list(self):
        list_ = List.objects.create()
        form = ItemForm(data={"text": "chocolate"})
        new_item = form.save(for_list=list_)
        self.assertEqual(new_item, Item.objects.first())
        self.assertEqual(new_item.text, "chocolate")
        self.assertEqual(new_item.list, list_)

    def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text="lqlq")
        response = self.client.post(
            "/lists/%d/" % (list1.id),
            data={"text": "lqlq"}
        )
        expected_error = escape(DUPLICATE_ITEM_ERROR)
        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, "list.html")
        self.assertEqual(Item.objects.all().count(), 1)

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context["form"], ExistingListItemForm)


class NewListTest(TestCase):
    def test_redirects_after_POST(self):
        response = self.client.post(
            "/lists/new",
            data={"text": "A new item for an excisting list"}
        )
        new_list = List.objects.first()
        self.assertRedirects(response, "/lists/%d/" % (new_list.id,))

    def test_for_invalid_input_renders_home_template(self):
        response = self.client.post("/lists/new", data={"text": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertIsInstance(response.context["form"], ItemForm)

    def test_validation_errors_are_shown_on_home_page(self):
        response = self.client.post("/lists/new", data={"text": ""})
        self.assertContains(response, escape(EMPTY_LIST_ERROR))

    def test_invalid_list_items_arent_saved(self):
        self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)
