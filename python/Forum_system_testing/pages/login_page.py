from selenium.webdriver.common.by import By

from common.base_page import BasePage
from config import settings


class LoginPage(BasePage):
    DIALOG_HEADING = "登陆"
    USERNAME_INPUT = (By.CSS_SELECTOR, "#username")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "#password")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "#submit")
    LOGIN_DIALOG = (By.CSS_SELECTOR, ".login-dialog")
    DIALOG_TITLE = (By.CSS_SELECTOR, ".login-dialog h3")

    def open(self):
        super().open(settings.SIGN_IN_URL)
        self.find(*self.LOGIN_DIALOG)

    def dialog_heading(self):
        return self.text_of(*self.DIALOG_TITLE).strip()

    def clear_token(self):
        if not (self.driver.current_url or "").startswith(settings.BASE_URL):
            super().open(settings.SIGN_IN_URL)
        self.driver.execute_script("localStorage.removeItem('user_token');")

    def token(self):
        return self.driver.execute_script("return localStorage.getItem('user_token');")

    def open_as_guest(self, url):
        self.clear_token()
        self.driver.get(url)
        self.wait_url_contains("blog_login.html")
        self.find(*self.LOGIN_DIALOG)
        return self.driver.current_url

    def login(self, username, password):
        self.input_text(*self.USERNAME_INPUT, value=username)
        self.input_text(*self.PASSWORD_INPUT, value=password)
        self.js_click(*self.SUBMIT_BUTTON)

    def login_success(self, username=settings.USERNAME, password=settings.PASSWORD):
        self.login(username, password)
        self.wait_url_contains("blog_list.html")

    def login_fail(self, username=settings.USERNAME, password=settings.WRONG_PASSWORD):
        self.capture_alert()
        self.login(username, password)
        return self.wait_dialog_message().strip()
