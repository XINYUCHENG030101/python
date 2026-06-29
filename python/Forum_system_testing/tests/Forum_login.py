from common.base_case import BaseCase
from pages.login_page import LoginPage


class ForumLoginTest(BaseCase):
    def setUp(self):
        self.page = LoginPage(self.driver)
        self.page.open()

    def test_login_success(self):
        self.page.login_success()
        self.assertTrue(self.page.is_present(*self.page.LOGIN_SUCCESS_MARK))

    def test_login_fail(self):
        message = self.page.login_fail()
        self.assertIn("用户名或密码错误", message)
