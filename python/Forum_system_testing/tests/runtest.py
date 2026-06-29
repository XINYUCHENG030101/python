import os
import unittest

from common.report import ReportTextRunner
from tests.Forum_details import ForumDetailsTest
from tests.Forum_edit import ForumEditTest
from tests.Forum_list import ForumListTest
from tests.Forum_login import ForumLoginTest


def build_suite():
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader

    available = {
        "login": ForumLoginTest,
        "list": ForumListTest,
        "edit": ForumEditTest,
        "details": ForumDetailsTest,
    }

    selected = os.getenv("FORUM_SUITE", "all").lower()
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
   

