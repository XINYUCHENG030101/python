import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT_DIR / "images"
REPORTS_DIR = ROOT_DIR / "reports"
LOGS_DIR = ROOT_DIR / "logs"

load_dotenv(ROOT_DIR / ".env")

BASE_URL = os.getenv("FORUM_BASE_URL", "http://127.0.0.1:9580").rstrip("/")
BROWSER = os.getenv("FORUM_BROWSER", "chrome").lower()
HEADLESS = os.getenv("FORUM_HEADLESS", "false").lower() == "true"
IMPLICIT_WAIT = int(os.getenv("FORUM_IMPLICIT_WAIT", "5"))
EXPLICIT_WAIT = int(os.getenv("FORUM_EXPLICIT_WAIT", "10"))
WINDOW_WIDTH = int(os.getenv("FORUM_WINDOW_WIDTH", "1440"))
WINDOW_HEIGHT = int(os.getenv("FORUM_WINDOW_HEIGHT", "900"))
REPORT_NAME = os.getenv("FORUM_REPORT_NAME", "ui_test_report.html")
LOG_FILE_NAME = os.getenv("FORUM_LOG_FILE", "framework.log")

USERNAME = os.getenv("FORUM_USERNAME", "zhangsan")
PASSWORD = os.getenv("FORUM_PASSWORD", "123")
WRONG_PASSWORD = os.getenv("FORUM_WRONG_PASSWORD", "1234")

SIGN_IN_URL = f"{BASE_URL}/sign-in.html"
INDEX_URL = f"{BASE_URL}/index.html"

REPORT_FILE = REPORTS_DIR / REPORT_NAME
LOG_FILE = LOGS_DIR / LOG_FILE_NAME
