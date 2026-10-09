from common.base_case import BaseCase
from config import settings
from pages.blog_edit_page import BlogEditPage
from pages.blog_list_page import BlogListPage
from pages.login_page import LoginPage


class BlogListTest(BaseCase):
    def setUp(self):
        super().setUp()
        LoginPage(self.driver).open()
        LoginPage(self.driver).login_success()
        self.page = BlogListPage(self.driver)
        self.page.wait_for_blogs()

    def test_list_content(self):
        self.assertEqual(self.page.site_name(), self.page.SITE_NAME)
        blogs = self.page.iter_blogs()
        self.assertGreaterEqual(len(blogs), 1)
        for blog in blogs:
            self.assertTrue(blog["title"])
            self.assertRegex(blog["date"], BlogListPage.TIME_PATTERN)
            self.assertTrue(blog["desc"])
            self.assertIn("blog_detail.html", blog["href"])
            self.assertIn("blogId=", blog["href"])
        self.assertEqual(self.page.get_user_name(), settings.USERNAME)
        self.assertTrue(self.page.get_github_url().startswith("https://"))

    def test_open_editor_from_nav(self):
        self.page.go_write_blog()
        editor = BlogEditPage(self.driver)
        self.assertIn("blog_edit.html", self.driver.current_url)
        self.assertTrue(editor.is_present(*editor.TITLE_INPUT))
        self.assertEqual(editor.submit_label(), editor.SUBMIT_LABEL)
