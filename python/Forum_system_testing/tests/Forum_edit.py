from common.base_case import BaseCase
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.post_edit_page import PostEditPage


class ForumEditTest(BaseCase):
    def setUp(self):
        self.login_page = LoginPage(self.driver)
        self.login_page.open()
        self.login_page.login_success()
        self.home_page = HomePage(self.driver)
        self.home_page.open()
        self.page = PostEditPage(self.driver)

    def test_publish_post(self):
        self.home_page.open_post_editor()
        self.page.publish_post("自动化测试")
        self.assertTrue(self.page.driver.current_url)
