from common.base_case import BaseCase
from pages.home_page import HomePage
from pages.login_page import LoginPage


class ForumListTest(BaseCase):
    def setUp(self):
        LoginPage(self.driver).open()
        LoginPage(self.driver).login_success()
        self.page = HomePage(self.driver)
        self.page.open()

    def test_list_content(self):
        title, meta = self.page.get_first_post_summary()
        self.assertTrue(title.strip())
        self.assertTrue(meta.strip())
        self.assertTrue(self.page.is_present(*self.page.USER_AVATAR))

    def test_search_and_theme_switch(self):
        self.page.search("111")
        self.page.toggle_theme()
        self.assertTrue(self.page.is_present(*self.page.USER_AVATAR))
