from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from config import settings


def _local_chromedriver():
    driver_dir = Path(settings.ROOT_DIR) / ".drivers"
    direct = driver_dir / "chromedriver.exe"
    if direct.exists():
        return str(direct)

    nested = list(driver_dir.glob("**/chromedriver.exe"))
    if nested:
        return str(nested[0])
    return None


def create_driver():
    if settings.BROWSER != "chrome":
        raise ValueError(f"Unsupported browser: {settings.BROWSER}")

    options = webdriver.ChromeOptions()
    options.add_argument(f"--window-size={settings.WINDOW_WIDTH},{settings.WINDOW_HEIGHT}")
    options.add_argument("--force-device-scale-factor=1")
    options.add_argument("--high-dpi-support=1")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        },
    )

    if settings.HEADLESS:
        options.add_argument("--headless=new")

    driver_path = _local_chromedriver()
    if driver_path:
        driver = webdriver.Chrome(service=Service(driver_path), options=options)
    else:
        driver = webdriver.Chrome(options=options)

    driver.implicitly_wait(settings.IMPLICIT_WAIT)
    return driver
