import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import settings


class BasePage:
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

    def input_text(self, by, locator, value, clear_first=True):
        element = self.find(by, locator)
        if clear_first:
            element.clear()
        element.send_keys(value)
        return element

    def text_of(self, by, locator):
        return self.find(by, locator).text

    def is_present(self, by, locator):
        try:
            self.wait.until(EC.presence_of_element_located((by, locator)))
            return True
        except Exception:
            return False

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
