from common.base_case import BaseCase
from config import settings
from pages.blog_detail_page import BlogDetailPage
from pages.blog_list_page import BlogListPage
from pages.login_page import LoginPage


class BlogDetailsTest(BaseCase):
    def setUp(self):
        super().setUp()
        self.login_page = LoginPage(self.driver)
        self.login_page.open()
        self.login_page.login_success()
        self.list_page = BlogListPage(self.driver)
        self.list_page.wait_for_blogs()
        self.page = BlogDetailPage(self.driver)

    def test_blog_details_and_back_home(self):
        expected_title, expected_date, expected_desc = self.list_page.get_first_blog_summary()
        self.assertRegex(expected_date, BlogListPage.TIME_PATTERN)
        expected_href = self.list_page.first_detail_url()
        self.list_page.open_first_blog()
        self.assertEqual(self.driver.current_url.split("#")[0], expected_href.split("#")[0])
        self.assertTrue(self.page.current_blog_id().isdigit())
        self.assertEqual(self.page.get_title(), expected_title)
        self.assertEqual(self.page.get_date(), expected_date)
        body = self.page.get_body()
        fragments = self.page.visible_fragments(expected_desc)
        self.assertTrue(fragments)
        for fragment in fragments:
            self.assertIn(fragment, body)
        self.assertEqual(self.page.wait_profile_name(settings.USERNAME), settings.USERNAME)
        self.assertTrue(self.page.get_github_url().startswith("https://"))
        self.assertEqual(self.page.owner_actions(), ["编辑", "删除"])
        self.page.go_home()
        self.assertIn("blog_list.html", self.driver.current_url)
        self.assertEqual(self.list_page.get_first_blog_summary()[0], expected_title)
