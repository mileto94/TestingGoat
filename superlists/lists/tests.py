from django.core.urlresolvers import resolve
from django.test import TestCase
from lists.views import home_page
from django.http import HttpRequest
from django.template.loader import render_to_string
from lists.models import Item, List
from django.core.exceptions import ValidationError
from django.utils.html import escape


class HomePageTest(TestCase):
    def test_root_url_resolves_to_home_page_view(self):
        found = resolve("/")
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_real_html(self):
        request = HttpRequest()
        response = home_page(request)
        expected_html = render_to_string("home.html")
        self.assertEqual(response.content.decode(), expected_html)


class ListsAndItemModelsTest(TestCase):
    def test_saving_and_retrieving_items(self):
        list_ = List()
        list_.save()

        first_item = Item()
        first_item.text = "First list item"
        first_item.list = list_
        first_item.save()

        second_item = Item()
        second_item.text = "Second item"
        second_item.list = list_
        second_item.save()

        saved_list = List.objects.first()
        self.assertEqual(saved_list, list_)

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text, "First list item")
        self.assertEqual(first_saved_item.list, list_)
        self.assertEqual(second_saved_item.text, "Second item")
        self.assertEqual(second_saved_item.list, list_)

    def test_cannot_save_empty_list_item(self):
        list_ = List.objects.create()
        item = Item(list=list_, text="")
        with self.assertRaises(ValidationError):
            item.save()
            item.full_clean()


class ListViewTest(TestCase):
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
            "/lists/%d/add_item" % (correct_list.id,),
            data={"item_text": "A new item for an excisting list"}
        )
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new item for an excisting list")
        self.assertEqual(new_item.list, correct_list)

    def test_redirects_after_POST(self):
        correct_list = List.objects.create()

        response = self.client.post(
            "/lists/%d/add_item" % (correct_list.id,),
            data={"item_text": "A new item for an excisting list"}
        )
        self.assertRedirects(response, "/lists/%d/" % (correct_list.id,))


# class NewListTest(TestCase):
    def test_validation_errors_are_send_back_to_home_page_template(self):
        response = self.client.post("/lists/new", data={"item_text": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        expected_error = escape("You can't have an empty list item")
        self.assertContains(response, expected_error)

    def test_invalid_items_arent_saved(self):
        self.client.post("/lists/new", data={"item_text": ""})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)
