from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config import settings


def create_driver():
    if settings.BROWSER != "chrome":
        raise ValueError(f"Unsupported browser: {settings.BROWSER}")

    options = webdriver.ChromeOptions()
    options.add_argument(f"--window-size={settings.WINDOW_WIDTH},{settings.WINDOW_HEIGHT}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    if settings.HEADLESS:
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    driver.implicitly_wait(settings.IMPLICIT_WAIT)
    return driver
