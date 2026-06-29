from common.base_case import BaseCase
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.post_detail_page import PostDetailPage


class ForumDetailsTest(BaseCase):
    def setUp(self):
        self.login_page = LoginPage(self.driver)
        self.login_page.open()
        self.login_page.login_success()
        self.home_page = HomePage(self.driver)
        self.home_page.open()
        self.page = PostDetailPage(self.driver)

    def test_post_details_actions(self):
        self.home_page.open_first_post()
        self.page.like_post()
        self.page.switch_board()
        self.assertTrue(self.page.driver.current_url)
