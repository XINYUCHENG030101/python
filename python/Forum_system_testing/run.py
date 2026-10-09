import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser(description="运行博客系统 UI 自动化测试")
    parser.add_argument("--suite", default=None, help="指定测试套件: login/list/edit/details/all")
    parser.add_argument("--base-url", default=None, help="指定被测系统地址")
    parser.add_argument("--headless", action="store_true", help="是否启用无头模式")
    parser.add_argument("--report-name", default=None, help="指定报告文件名")
    return parser.parse_args()


def apply_runtime_args(args):
    if args.suite:
        os.environ["BLOG_SUITE"] = args.suite
    if args.base_url:
        os.environ["BLOG_BASE_URL"] = args.base_url
    if args.headless:
        os.environ["BLOG_HEADLESS"] = "true"
    if args.report_name:
        os.environ["BLOG_REPORT_NAME"] = args.report_name


if __name__ == "__main__":
    args = parse_args()
    apply_runtime_args(args)

    from common.logger import get_logger, init_logging
    from common.report import ReportTextRunner, generate_html_report, now
    from tests.runtest import build_suite

    init_logging()
    logger = get_logger("runner")
    started_at = now()
    logger.info("开始执行博客系统 UI 自动化测试")

    runner = ReportTextRunner(verbosity=2)
    result = runner.run(build_suite())

    report_file = generate_html_report(result, started_at, now())
    logger.info("测试执行结束，报告生成位置: %s", report_file)
    raise SystemExit(0 if result.wasSuccessful() else 1)
