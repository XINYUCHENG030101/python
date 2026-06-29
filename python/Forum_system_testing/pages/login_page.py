from selenium.webdriver.common.by import By

from common.base_page import BasePage
from config import settings


class LoginPage(BasePage):
    USERNAME_INPUT = (By.CSS_SELECTOR, "#username")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "#password")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "#submit")
    ERROR_TOAST = (By.CSS_SELECTOR, "body > div.jq-toast-wrap.bottom-right > div")
    ERROR_TOAST_CLOSE = (By.CLASS_NAME, "close-jq-toast-single")
    LOGIN_SUCCESS_MARK = (By.CSS_SELECTOR, "#index_nav_avatar")

    def open(self):
        super().open(settings.SIGN_IN_URL)

    def login(self, username, password):
        self.input_text(*self.USERNAME_INPUT, value=username)
        self.input_text(*self.PASSWORD_INPUT, value=password)
        self.click(*self.SUBMIT_BUTTON)

    def login_success(self, username=settings.USERNAME, password=settings.PASSWORD):
        self.login(username, password)
        self.find(*self.LOGIN_SUCCESS_MARK)

    def login_fail(self, username=settings.USERNAME, password=settings.WRONG_PASSWORD):
        self.login(username, password)
        toast = self.find(*self.ERROR_TOAST)
        message = toast.text
        toast.find_element(*self.ERROR_TOAST_CLOSE).click()
        return message
