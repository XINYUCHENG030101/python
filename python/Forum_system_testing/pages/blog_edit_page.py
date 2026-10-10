from selenium.webdriver.common.by import By

from common.base_page import BasePage
from config import settings
from pages.markdown_editor import set_markdown, type_markdown


class BlogEditPage(BasePage):
    TITLE_INPUT = (By.CSS_SELECTOR, "#title")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "#submit")
    EDITOR = (By.CSS_SELECTOR, "#editor")
    CONTENT_TEXTAREA = (By.CSS_SELECTOR, "#content")
    SUBMIT_LABEL = "发布文章"

    def open(self):
        super().open(settings.EDIT_URL)
        self.find(*self.TITLE_INPUT)

    def set_content(self, content):
        set_markdown(self.driver, content)

    def type_content(self, content):
        return type_markdown(self.driver, content)

    def submit_label(self):
        return self.find(*self.SUBMIT_BUTTON).get_attribute("value")

    def fill_and_submit(self, title, content):
        self.find(*self.TITLE_INPUT)
        self.input_text(*self.TITLE_INPUT, value=title)
        self.set_content(content)
        self.submit()

    def submit(self):
        self.js_click(*self.SUBMIT_BUTTON)

    def submit_and_get_message(self):
        self.capture_alert()
        self.submit()
        return self.wait_dialog_message()

    def publish_blog(self, title, content="## 由 UI 自动化测试发布"):
        self.fill_and_submit(title, content)
        self.wait_url_contains("blog_list.html")

    def publish_typed_blog(self, title, content):
        self.find(*self.TITLE_INPUT)
        self.input_text(*self.TITLE_INPUT, value=title)
        typed = self.type_content(content)
        self.submit()
        self.wait_url_contains("blog_list.html")
        return typed
