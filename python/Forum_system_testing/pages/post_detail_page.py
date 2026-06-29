from selenium.webdriver.common.by import By

from common.base_page import BasePage


class PostDetailPage(BasePage):
    LIKE_BUTTON = (By.CSS_SELECTOR, "#details_btn_like_count")
    BOARD_TAB = (By.CSS_SELECTOR, "#topBoardList > li:nth-child(2) > a > span.nav-link-title")

    def like_post(self):
        self.click(*self.LIKE_BUTTON)

    def switch_board(self):
        self.click(*self.BOARD_TAB)
