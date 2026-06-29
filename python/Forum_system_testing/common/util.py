from common.driver_factory import create_driver


class Driver:
    def __init__(self):
        self.driver = create_driver()

    def getscreenshot(self, name="legacy_screenshot"):
        from common.base_page import BasePage

        page = BasePage(self.driver)
        return page.screenshot(name)


ForumDriver = Driver()
