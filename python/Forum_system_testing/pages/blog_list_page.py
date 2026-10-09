from selenium.webdriver.common.by import By

from common.base_page import BasePage
from config import settings


def xpath_literal(value):
    if "'" not in value:
        return f"'{value}'"
    if '"' not in value:
        return f'"{value}"'
    pieces = value.split("'")
    return "concat('" + "', \"'\", '".join(pieces) + "')"


class BlogListPage(BasePage):
    TIME_PATTERN = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"
    BLOG_ITEM = (By.CSS_SELECTOR, ".container .right .blog")
    FIRST_BLOG_TITLE = (By.CSS_SELECTOR, ".container .right .blog .title")
    FIRST_BLOG_DATE = (By.CSS_SELECTOR, ".container .right .blog .date")
    FIRST_BLOG_DESC = (By.CSS_SELECTOR, ".container .right .blog .desc")
    FIRST_BLOG_DETAIL_LINK = (By.CSS_SELECTOR, ".container .right .blog a.detail")
    USER_NAME = (By.CSS_SELECTOR, ".left .card h3")
    BLOG_TITLES = (By.CSS_SELECTOR, ".container .right .blog .title")

    def open(self):
        super().open(settings.INDEX_URL)
        self.wait_for_blogs()

    def wait_for_blogs(self):
        self.find(*self.BLOG_ITEM)
        return self

    def get_first_blog_summary(self):
        self.wait_for_blogs()
        title = self.text_of(*self.FIRST_BLOG_TITLE).strip()
        date = self.text_of(*self.FIRST_BLOG_DATE).strip()
        desc = self.text_of(*self.FIRST_BLOG_DESC).strip()
        return title, date, desc

    def first_detail_url(self):
        self.wait_for_blogs()
        return self.find(*self.FIRST_BLOG_DETAIL_LINK).get_attribute("href")

    def iter_blogs(self):
        self.wait_for_blogs()
        blogs = []
        for element in self.find_all(*self.BLOG_ITEM):
            blogs.append(
                {
                    "title": element.find_element(By.CSS_SELECTOR, ".title").text.strip(),
                    "date": element.find_element(By.CSS_SELECTOR, ".date").text.strip(),
                    "desc": element.find_element(By.CSS_SELECTOR, ".desc").text.strip(),
                    "href": element.find_element(By.CSS_SELECTOR, "a.detail").get_attribute("href"),
                }
            )
        return blogs

    def get_all_titles(self):
        self.wait_for_blogs()
        return [element.text.strip() for element in self.find_all(*self.BLOG_TITLES)]

    def get_user_name(self):
        return self.wait_profile_name(settings.USERNAME)

    def _blog_xpath(self, title):
        return (
            "//div[@class='blog']"
            f"[div[@class='title' and normalize-space()={xpath_literal(title)}]]"
        )

    def get_desc_by_title(self, title):
        locator = (By.XPATH, self._blog_xpath(title) + "/div[@class='desc']")
        return self.text_of(*locator).strip()

    def get_date_by_title(self, title):
        locator = (By.XPATH, self._blog_xpath(title) + "/div[@class='date']")
        return self.text_of(*locator).strip()

    def _visible_titles(self):
        self.driver.implicitly_wait(0)
        try:
            return [element.text.strip() for element in self.driver.find_elements(*self.BLOG_TITLES)]
        finally:
            self.driver.implicitly_wait(settings.IMPLICIT_WAIT)

    def wait_title_present(self, title):
        self.wait.until(lambda driver: title in self._visible_titles())

    def wait_title_absent(self, title):
        def _gone(driver):
            titles = self._visible_titles()
            return bool(titles) and title not in titles

        self.wait.until(_gone)

    def open_first_blog(self):
        self.open_href(*self.FIRST_BLOG_DETAIL_LINK, fragment="blog_detail.html")

    def open_blog_by_title(self, title):
        locator = (By.XPATH, self._blog_xpath(title) + "/a[@class='detail']")
        self.open_href(*locator, fragment="blog_detail.html")
