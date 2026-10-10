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
AI_FAILURES_DIR = REPORTS_DIR / "ai_failures"

AI_ENABLED = os.getenv("BLOG_AI_ENABLED", "false").lower() == "true"
AI_BASE_URL = os.getenv("BLOG_AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
AI_API_KEY = os.getenv("BLOG_AI_API_KEY", "")
AI_MODEL = os.getenv("BLOG_AI_MODEL", "gpt-4o-mini")
AI_TIMEOUT = int(os.getenv("BLOG_AI_TIMEOUT", "60"))
AI_FAILURE_ANALYSIS = os.getenv("BLOG_AI_FAILURE_ANALYSIS", "true").lower() == "true"
AI_REPORT_SUMMARY = os.getenv("BLOG_AI_REPORT_SUMMARY", "true").lower() == "true"
AI_UPLOAD_SCREENSHOT = os.getenv("BLOG_AI_UPLOAD_SCREENSHOT", "false").lower() == "true"
AI_LOG_TAIL_LINES = int(os.getenv("BLOG_AI_LOG_TAIL_LINES", "80"))
AI_GEN_DATA = os.getenv("BLOG_AI_GEN_DATA", "false").lower() == "true"
AI_HEALER = os.getenv("BLOG_AI_HEALER", "false").lower() == "true"
AI_HEALER_DOM_CHARS = int(os.getenv("BLOG_AI_HEALER_DOM_CHARS", "12000"))
AI_DATA_CONTENT_MAX = int(os.getenv("BLOG_AI_DATA_CONTENT_MAX", "120"))
AI_HEALER_DIR = REPORTS_DIR / "ai_healer"
