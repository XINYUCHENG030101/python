import os
import unittest

from common.report import ReportTextRunner
from tests.Blog_details import BlogDetailsTest
from tests.Blog_edit import BlogEditTest
from tests.Blog_list import BlogListTest
from tests.Blog_login import BlogLoginTest


def build_suite():
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader

    available = {
        "login": BlogLoginTest,
        "list": BlogListTest,
        "edit": BlogEditTest,
        "details": BlogDetailsTest,
    }

    selected = os.getenv("BLOG_SUITE", "all").lower()
    if selected == "all":
        for case in available.values():
            suite.addTests(loader.loadTestsFromTestCase(case))
        return suite

    if selected not in available:
        raise ValueError(f"Unsupported suite: {selected}")

    suite.addTests(loader.loadTestsFromTestCase(available[selected]))
    return suite


if __name__ == "__main__":
    runner = ReportTextRunner(verbosity=2)
    result = runner.run(build_suite())
    raise SystemExit(0 if result.wasSuccessful() else 1)
