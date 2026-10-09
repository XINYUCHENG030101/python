import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT_DIR / "images"
REPORTS_DIR = ROOT_DIR / "reports"
LOGS_DIR = ROOT_DIR / "logs"

load_dotenv(ROOT_DIR / ".env")

BASE_URL = os.getenv("BLOG_BASE_URL", "http://115.190.63.202:9090").rstrip("/")
BROWSER = os.getenv("BLOG_BROWSER", "chrome").lower()
HEADLESS = os.getenv("BLOG_HEADLESS", "false").lower() == "true"
IMPLICIT_WAIT = int(os.getenv("BLOG_IMPLICIT_WAIT", "5"))
EXPLICIT_WAIT = int(os.getenv("BLOG_EXPLICIT_WAIT", "10"))
WINDOW_WIDTH = int(os.getenv("BLOG_WINDOW_WIDTH", "1440"))
WINDOW_HEIGHT = int(os.getenv("BLOG_WINDOW_HEIGHT", "900"))
REPORT_NAME = os.getenv("BLOG_REPORT_NAME", "ui_test_report.html")
LOG_FILE_NAME = os.getenv("BLOG_LOG_FILE", "framework.log")

USERNAME = os.getenv("BLOG_USERNAME", "zhangsan")
PASSWORD = os.getenv("BLOG_PASSWORD", "123456")
WRONG_PASSWORD = os.getenv("BLOG_WRONG_PASSWORD", "123")
UNKNOWN_USERNAME = os.getenv("BLOG_UNKNOWN_USERNAME", "zhangsa")

SIGN_IN_URL = f"{BASE_URL}/blog_login.html"
INDEX_URL = f"{BASE_URL}/blog_list.html"
EDIT_URL = f"{BASE_URL}/blog_edit.html"
UPDATE_URL = f"{BASE_URL}/blog_update.html"
DETAIL_URL = f"{BASE_URL}/blog_detail.html"

REPORT_FILE = REPORTS_DIR / REPORT_NAME
LOG_FILE = LOGS_DIR / LOG_FILE_NAME
