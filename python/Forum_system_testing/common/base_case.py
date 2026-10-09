import unittest

from common.base_page import BasePage
from common.driver_factory import create_driver
from common.logger import get_logger


class BaseCase(unittest.TestCase):
    driver = None

    @classmethod
    def setUpClass(cls):
        cls.logger = get_logger(cls.__name__)
        cls.logger.info("初始化浏览器驱动")
        cls.driver = create_driver()

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.logger.info("关闭浏览器驱动")
            cls.driver.quit()
            cls.driver = None

    def setUp(self):
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info("开始执行用例: %s", self.id())

    def save_failure_screenshot(self):
        page = getattr(self, "page", None) or BasePage(self.driver)
        file_path = page.screenshot(self.id().split(".")[-1])
        self.logger.error("用例失败，已截图: %s", file_path)

    def run(self, result=None):
        super().run(result)
        if result is None:
            return

        failure_entries = list(result.failures) + list(result.errors)
        for test_case, _ in failure_entries:
            if test_case is self:
                self.save_failure_screenshot()
                break
        else:
            self.logger.info("用例执行完成: %s", self.id())
