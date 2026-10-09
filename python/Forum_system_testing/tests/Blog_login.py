from datetime import datetime

from common.base_case import BaseCase
from config import settings
from pages.blog_edit_page import BlogEditPage
from pages.blog_list_page import BlogListPage
from pages.login_page import LoginPage


class BlogLoginTest(BaseCase):
    def setUp(self):
        super().setUp()
        self.page = LoginPage(self.driver)
        self.page.open()
        self.page.clear_token()

    def test_login_success(self):
        self.page.login_success()
        self.assertIn("blog_list.html", self.driver.current_url)
        self.assertEqual(self.page.site_name(), self.page.SITE_NAME)
        token = self.page.token()
        self.assertRegex(token or "", r"^.+\..+\..+$")

    def test_login_fail(self):
        message = self.page.login_fail()
        self.assertEqual(message, "密码错误")
        self.assertIn("blog_login.html", self.driver.current_url)
        self.assertEqual(self.page.dialog_heading(), self.page.DIALOG_HEADING)
        self.assertIsNone(self.page.token())

    def test_login_unknown_user(self):
        message = self.page.login_fail(username=settings.UNKNOWN_USERNAME, password=settings.PASSWORD)
        self.assertEqual(message, "用户不存在")
        self.assertIn("blog_login.html", self.driver.current_url)
        self.assertEqual(self.page.dialog_heading(), self.page.DIALOG_HEADING)
        self.assertIsNone(self.page.token())

    def test_login_empty_username(self):
        message = self.page.login_fail(username="", password=settings.PASSWORD)
        self.assertEqual(message, "账号或密码不能为空")
        self.assertIn("blog_login.html", self.driver.current_url)
        self.assertIsNone(self.page.token())

    def test_login_empty_password(self):
        message = self.page.login_fail(username=settings.USERNAME, password="")
        self.assertEqual(message, "账号或密码不能为空")
        self.assertIn("blog_login.html", self.driver.current_url)
        self.assertIsNone(self.page.token())

    def test_guest_list_redirects_to_login(self):
        current_url = self.page.open_as_guest(settings.INDEX_URL)
        self.assertIn("blog_login.html", current_url)
        self.assertEqual(self.page.dialog_heading(), self.page.DIALOG_HEADING)
        self.assertIsNone(self.page.token())

    def test_guest_detail_redirects_to_login(self):
        current_url = self.page.open_as_guest(f"{settings.DETAIL_URL}?blogId=1")
        self.assertIn("blog_login.html", current_url)
        self.assertEqual(self.page.dialog_heading(), self.page.DIALOG_HEADING)

    def test_guest_update_redirects_to_login(self):
        current_url = self.page.open_as_guest(f"{settings.UPDATE_URL}?blogId=1")
        self.assertIn("blog_login.html", current_url)
        self.assertEqual(self.page.dialog_heading(), self.page.DIALOG_HEADING)

    def test_guest_editor_submit_redirects_to_login(self):
        title = f"未登录提交-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        editor = BlogEditPage(self.driver)
        editor.open()
        self.assertIn("blog_edit.html", self.driver.current_url)
        editor.input_text(*editor.TITLE_INPUT, value=title)
        editor.submit()
        editor.wait_url_contains("blog_login.html")
        self.assertEqual(self.page.dialog_heading(), self.page.DIALOG_HEADING)
        self.page.login_success()
        self.assertNotIn(title, BlogListPage(self.driver).get_all_titles())

    def test_logout_then_list_requires_login(self):
        self.page.login_success()
        self.assertRegex(self.page.token() or "", r"^.+\..+\..+$")
        BlogListPage(self.driver).logout()
        self.assertIn("blog_login.html", self.driver.current_url)
        self.assertIsNone(self.page.token())
        current_url = self.page.open_as_guest(settings.INDEX_URL)
        self.assertIn("blog_login.html", current_url)
        self.assertEqual(self.page.dialog_heading(), self.page.DIALOG_HEADING)
