from selenium.webdriver.common.by import By

from common.base_page import BasePage


class PostEditPage(BasePage):
    TITLE_INPUT = (By.CSS_SELECTOR, "#article_post_title")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "#article_post_submit")

    def publish_post(self, title):
        self.input_text(*self.TITLE_INPUT, value=title)
        self.click(*self.SUBMIT_BUTTON)
