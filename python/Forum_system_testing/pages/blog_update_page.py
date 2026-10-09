from selenium.webdriver.common.by import By

from common.base_page import BasePage
from pages.markdown_editor import editor_content, set_markdown, wait_markdown_contains


class BlogUpdatePage(BasePage):
    BLOG_ID = (By.CSS_SELECTOR, "#blogId")
    TITLE_INPUT = (By.CSS_SELECTOR, "#title")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "#submit")
    SUBMIT_LABEL = "更新文章"

    def wait_loaded(self):
        self.wait_url_contains("blog_update.html")
        self.wait.until(
            lambda driver: (
                driver.find_element(*self.BLOG_ID).get_attribute("value") or ""
            ).strip()
        )
        self.find(*self.TITLE_INPUT)
        return self

    def get_blog_id(self):
        self.wait_loaded()
        return self.driver.find_element(*self.BLOG_ID).get_attribute("value").strip()

    def get_title(self):
        self.wait_loaded()
        return (self.find(*self.TITLE_INPUT).get_attribute("value") or "").strip()

    def wait_title(self, title):
        self.wait_loaded()
        self.wait.until(
            lambda driver: (
                driver.find_element(*self.TITLE_INPUT).get_attribute("value") or ""
            ).strip()
            == title
        )
        return self.get_title()

    def wait_content_contains(self, snippet):
        self.wait_loaded()
        return wait_markdown_contains(self.driver, snippet)

    def get_content(self):
        self.wait_loaded()
        return editor_content(self.driver)

    def submit_label(self):
        return self.find(*self.SUBMIT_BUTTON).get_attribute("value")

    def update_blog(self, title, content):
        self.wait_loaded()
        self.input_text(*self.TITLE_INPUT, value=title)
        set_markdown(self.driver, content)
        self.js_click(*self.SUBMIT_BUTTON)
        self.wait_url_contains("blog_list.html")
