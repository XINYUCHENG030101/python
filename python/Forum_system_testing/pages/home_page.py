from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from common.base_page import BasePage
from config import settings


class HomePage(BasePage):
    FIRST_POST_TITLE = (
        By.CSS_SELECTOR,
        "#artical-items-body > div:nth-child(2) > div > div.col > div.text-truncate > a > strong",
    )
    FIRST_POST_META = (
        By.CSS_SELECTOR,
        "#artical-items-body > div:nth-child(2) > div > div.col > div.text-muted.mt-2 > div > div.col > ul",
    )
    USER_AVATAR = (By.CSS_SELECTOR, "#index_nav_avatar")
    SEARCH_INPUT = (
        By.CSS_SELECTOR,
        "body > div.page > header.navbar.navbar-expand-md.navbar-light.d-print-none > div > div > div.nav-item.d-none.d-md-flex.me-3 > div > form > div > input",
    )
    THEME_SWITCH = (
        By.CSS_SELECTOR,
        "body > div.page > header.navbar.navbar-expand-md.navbar-light.d-print-none > div > div > div:nth-child(2) > a.nav-link.px-0.hide-theme-dark > svg",
    )
    POST_BUTTON = (
        By.CSS_SELECTOR,
        "#bit-forum-content > div.page-header.d-print-none > div > div > div.col-auto.ms-auto.d-print-none > div > a.btn.btn-primary.d-none.d-sm-inline-block.article_post",
    )

    def open(self):
        super().open(settings.INDEX_URL)

    def get_first_post_summary(self):
        title = self.text_of(*self.FIRST_POST_TITLE)
        meta = self.text_of(*self.FIRST_POST_META)
        return title, meta

    def search(self, keyword):
        self.input_text(*self.SEARCH_INPUT, value=keyword)
        self.find(*self.SEARCH_INPUT).send_keys(Keys.RETURN)

    def toggle_theme(self):
        self.click(*self.THEME_SWITCH)

    def open_first_post(self):
        self.click(*self.FIRST_POST_TITLE)

    def open_post_editor(self):
        self.click(*self.POST_BUTTON)
