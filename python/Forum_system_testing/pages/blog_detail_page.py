from urllib.parse import parse_qs, urlparse

from selenium.webdriver.common.by import By

from common.base_page import BasePage
from config import settings


class BlogDetailPage(BasePage):
    TITLE = (By.CSS_SELECTOR, ".content .title")
    DATE = (By.CSS_SELECTOR, ".content .date")
    BODY = (By.CSS_SELECTOR, "#detail")
    OPERATING = (By.CSS_SELECTOR, ".content .operating")
    ACTION_BUTTONS = (By.CSS_SELECTOR, ".content .operating button")
    EDIT_BUTTON = (By.XPATH, "//div[contains(@class,'operating')]//button[normalize-space()='编辑']")
    DELETE_BUTTON = (By.XPATH, "//div[contains(@class,'operating')]//button[normalize-space()='删除']")
    DELETE_CONFIRM = "确定删除?"

    def wait_for_content(self):
        self.wait_text_non_empty(*self.TITLE)
        return self

    def get_title(self):
        return self.wait_text_non_empty(*self.TITLE).strip()

    def get_date(self):
        return self.wait_text_non_empty(*self.DATE).strip()

    def get_body(self):
        self.wait_for_content()
        return self.text_of(*self.BODY).strip()

    def current_blog_id(self):
        self.wait_url_contains("blogId=")
        blog_ids = parse_qs(urlparse(self.driver.current_url).query).get("blogId") or []
        if not blog_ids or not blog_ids[0].strip():
            raise AssertionError(f"详情地址缺少 blogId: {self.driver.current_url}")
        return blog_ids[0].strip()

    def owner_actions(self):
        self.wait_for_content()

        def _labels(driver):
            driver.implicitly_wait(0)
            try:
                return [element.text.strip() for element in driver.find_elements(*self.ACTION_BUTTONS)]
            finally:
                driver.implicitly_wait(settings.IMPLICIT_WAIT)

        self.wait.until(lambda driver: len(_labels(driver)) >= 2)
        return _labels(self.driver)

    def open_editor(self):
        self.js_click(*self.EDIT_BUTTON)
        self.wait_url_contains("blog_update.html")

    def delete_and_confirm(self):
        self.capture_confirm_accept()
        self.js_click(*self.DELETE_BUTTON)
        message = self.wait_dialog_message().strip()
        self.wait_url_contains("blog_list.html")
        return message

    @staticmethod
    def visible_fragments(raw_content):
        fragments = []
        for line in (raw_content or "").splitlines():
            cleaned = line.strip()
            while cleaned.startswith("#"):
                cleaned = cleaned[1:].strip()
            if cleaned:
                fragments.append(cleaned)
        return fragments
