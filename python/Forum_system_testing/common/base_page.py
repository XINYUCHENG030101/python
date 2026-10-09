import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import settings


class BasePage:
    SITE_NAME = "我的博客系统"
    HOME_LINK = (By.CSS_SELECTOR, 'a.nav-span[href="blog_list.html"]')
    WRITE_LINK = (By.CSS_SELECTOR, 'a.nav-span[href="blog_edit.html"]')
    LOGOUT_LINK = (By.CSS_SELECTOR, 'a.nav-span[onclick="logout()"]')
    SITE_TITLE = (By.CSS_SELECTOR, ".blog-title")
    PROFILE_NAME = (By.CSS_SELECTOR, ".left .card h3")
    PROFILE_LINK = (By.CSS_SELECTOR, ".left .card a")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, settings.EXPLICIT_WAIT)

    def open(self, url):
        self.driver.get(url)

    def find(self, by, locator):
        return self.wait.until(EC.visibility_of_element_located((by, locator)))

    def find_all(self, by, locator):
        return self.wait.until(EC.presence_of_all_elements_located((by, locator)))

    def click(self, by, locator):
        self.wait.until(EC.element_to_be_clickable((by, locator))).click()

    def js_click(self, by, locator):
        element = self.wait.until(EC.element_to_be_clickable((by, locator)))
        self.driver.execute_script("arguments[0].click();", element)
        return element

    def open_href(self, by, locator, fragment):
        element = self.wait.until(EC.element_to_be_clickable((by, locator)))
        href = element.get_attribute("href")
        if not href or href.endswith("#"):
            raise AssertionError(f"无法通过 href 打开: {locator}")
        self.driver.get(href)
        self.wait_url_contains(fragment)
        return self.driver.current_url

    def input_text(self, by, locator, value, clear_first=True):
        element = self.find(by, locator)
        if clear_first:
            element.clear()
        if value:
            element.send_keys(value)
        if (element.get_attribute("value") or "") != value:
            self.driver.execute_script(
                """
                arguments[0].focus();
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                """,
                element,
                value,
            )
        return element

    def text_of(self, by, locator):
        return self.find(by, locator).text

    def is_present(self, by, locator):
        try:
            self.wait.until(EC.presence_of_element_located((by, locator)))
            return True
        except Exception:
            return False

    def wait_url_contains(self, fragment):
        self.wait.until(EC.url_contains(fragment))
        return self.driver.current_url

    def alert_text_and_accept(self):
        alert = self.wait.until(EC.alert_is_present())
        message = alert.text
        alert.accept()
        return message

    def capture_alert(self):
        self.driver.execute_script(
            """
            window.__dialogMessage = null;
            window.alert = function (message) { window.__dialogMessage = String(message); };
            """
        )

    def capture_confirm_accept(self):
        self.driver.execute_script(
            """
            window.__dialogMessage = null;
            window.confirm = function (message) {
                window.__dialogMessage = String(message);
                return true;
            };
            """
        )

    def wait_dialog_message(self):
        self.wait.until(
            lambda driver: driver.execute_script("return window.__dialogMessage;") is not None
        )
        return self.driver.execute_script("return window.__dialogMessage;")

    def wait_text_non_empty(self, by, locator):
        self.wait.until(
            lambda driver: driver.find_element(by, locator).text.strip()
        )
        return self.text_of(by, locator)

    def go_home(self):
        self.open_href(*self.HOME_LINK, fragment="blog_list.html")

    def go_write_blog(self):
        self.open_href(*self.WRITE_LINK, fragment="blog_edit.html")

    def logout(self):
        self.wait.until(EC.element_to_be_clickable(self.LOGOUT_LINK))
        self.driver.execute_script("logout()")
        self.wait_url_contains("blog_login.html")

    def site_name(self):
        return self.text_of(*self.SITE_TITLE).strip()

    def wait_profile_name(self, name):
        self.wait.until(
            lambda driver: driver.find_element(*self.PROFILE_NAME).text.strip() == name
        )
        return self.text_of(*self.PROFILE_NAME).strip()

    def get_github_url(self):
        self.wait.until(
            lambda driver: (
                driver.find_element(*self.PROFILE_LINK).get_attribute("href") or ""
            ).startswith("https://")
        )
        return self.driver.find_element(*self.PROFILE_LINK).get_attribute("href")

    def screenshot(self, name):
        date_folder = settings.IMAGES_DIR / datetime.datetime.now().strftime("%Y-%m-%d")
        date_folder.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        file_path = date_folder / f"{name}-{timestamp}.png"
        self.driver.save_screenshot(str(file_path))
        return file_path

    @staticmethod
    def css(locator):
        return By.CSS_SELECTOR, locator
