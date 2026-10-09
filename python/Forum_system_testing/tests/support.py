from selenium.common.exceptions import NoAlertPresentException

from pages.blog_detail_page import BlogDetailPage
from pages.blog_list_page import BlogListPage
from pages.markdown_editor import normalize_text


def dismiss_alert(driver):
    try:
        driver.switch_to.alert.accept()
    except NoAlertPresentException:
        return


def delete_titles(driver, titles, logger=None):
    page = BlogListPage(driver)
    for title in titles:
        if not title:
            continue
        try:
            dismiss_alert(driver)
            page.open()
            if title not in page.get_all_titles():
                continue
            page.open_blog_by_title(title)
            BlogDetailPage(driver).delete_and_confirm()
        except Exception as exc:
            if logger:
                logger.warning("清理博客失败 %s: %s", title, exc)
