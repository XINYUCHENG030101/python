from datetime import datetime

from common.base_case import BaseCase
from config import settings
from pages.blog_detail_page import BlogDetailPage
from pages.blog_edit_page import BlogEditPage
from pages.blog_list_page import BlogListPage
from pages.blog_update_page import BlogUpdatePage
from pages.login_page import LoginPage
from pages.markdown_editor import normalize_text
from tests.support import delete_titles


class BlogEditTest(BaseCase):
    def setUp(self):
        super().setUp()
        self.login_page = LoginPage(self.driver)
        self.login_page.open()
        self.login_page.login_success()
        self.list_page = BlogListPage(self.driver)
        self.list_page.wait_for_blogs()
        self.page = BlogEditPage(self.driver)
        self.detail_page = BlogDetailPage(self.driver)
        self.update_page = BlogUpdatePage(self.driver)

    def test_publish_blog(self):
        stamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        title = f"自动化测试-{stamp}"
        content = f"自动化正文-{stamp}"
        try:
            self.list_page.go_write_blog()
            self.page.publish_blog(title, content)
            self.list_page.wait_title_present(title)
            self.assertEqual(self.list_page.get_desc_by_title(title), content)
            self.assertRegex(self.list_page.get_date_by_title(title), BlogListPage.TIME_PATTERN)
        finally:
            delete_titles(self.driver, [title], self.logger)

    def test_publish_blog_by_typing(self):
        stamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        title = f"自动化测试-逐字-{stamp}"
        content = f"逐字正文-{stamp}"
        try:
            self.list_page.go_write_blog()
            typed = self.page.publish_typed_blog(title, content)
            self.assertEqual(normalize_text(typed), content)
            self.list_page.wait_title_present(title)
            self.assertEqual(self.list_page.get_desc_by_title(title), content)
            self.assertRegex(self.list_page.get_date_by_title(title), BlogListPage.TIME_PATTERN)
        finally:
            delete_titles(self.driver, [title], self.logger)

    def test_update_and_delete_own_blog(self):
        stamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        title = f"自动化测试-{stamp}"
        updated_title = f"自动化测试-已更新-{stamp}"
        content = f"自动化正文-{stamp}"
        updated_content = f"自动化正文已更新-{stamp}"
        try:
            self.list_page.go_write_blog()
            self.page.publish_blog(title, content)
            self.list_page.wait_title_present(title)
            created_date = self.list_page.get_date_by_title(title)
            self.assertEqual(self.list_page.get_desc_by_title(title), content)
            self.assertRegex(created_date, BlogListPage.TIME_PATTERN)

            self.list_page.open_blog_by_title(title)
            blog_id = self.detail_page.current_blog_id()
            self.assertEqual(self.detail_page.get_title(), title)
            self.assertEqual(self.detail_page.get_date(), created_date)
            self.assertIn(content, self.detail_page.get_body())
            self.assertEqual(self.detail_page.wait_profile_name(settings.USERNAME), settings.USERNAME)
            self.assertEqual(self.detail_page.owner_actions(), ["编辑", "删除"])

            self.detail_page.open_editor()
            self.assertIn(f"blogId={blog_id}", self.driver.current_url)
            self.assertEqual(self.update_page.wait_title(title), title)
            self.assertEqual(self.update_page.get_blog_id(), blog_id)
            self.assertEqual(self.update_page.submit_label(), self.update_page.SUBMIT_LABEL)
            loaded_content = self.update_page.wait_content_contains(content)
            self.assertEqual(normalize_text(loaded_content), content)

            self.update_page.update_blog(updated_title, updated_content)
            self.list_page.wait_title_present(updated_title)
            self.list_page.wait_title_absent(title)
            self.assertEqual(self.list_page.get_desc_by_title(updated_title), updated_content)
            self.assertEqual(self.list_page.get_date_by_title(updated_title), created_date)

            self.list_page.open_blog_by_title(updated_title)
            self.assertEqual(self.detail_page.current_blog_id(), blog_id)
            self.assertEqual(self.detail_page.get_title(), updated_title)
            self.assertEqual(self.detail_page.get_date(), created_date)
            self.assertIn(updated_content, self.detail_page.get_body())
            message = self.detail_page.delete_and_confirm()
            self.assertEqual(message, self.detail_page.DELETE_CONFIRM)
            self.list_page.wait_title_absent(updated_title)
            self.assertNotIn(title, self.list_page.get_all_titles())
        finally:
            delete_titles(self.driver, [title, updated_title], self.logger)
