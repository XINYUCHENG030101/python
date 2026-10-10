import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser(description="运行博客系统 UI 自动化测试")
    parser.add_argument("--suite", default=None, help="指定测试套件: login/list/edit/details/all")
    parser.add_argument("--base-url", default=None, help="指定被测系统地址")
    parser.add_argument("--headless", action="store_true", help="是否启用无头模式")
    parser.add_argument("--report-name", default=None, help="指定报告文件名")
    parser.add_argument(
        "--ai",
        action="store_true",
        help="启用 AI（需配置 BLOG_AI_API_KEY；具体子能力看 .env 开关）",
    )
    parser.add_argument(
        "--ai-gen-data",
        action="store_true",
        help="启用 AI 生成博客标题/正文（同时打开 BLOG_AI_ENABLED 与 BLOG_AI_GEN_DATA）",
    )
    parser.add_argument(
        "--ai-healer",
        action="store_true",
        help="启用定位器临时自愈建议（同时打开 BLOG_AI_ENABLED 与 BLOG_AI_HEALER）",
    )
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
    if args.ai or args.ai_gen_data or args.ai_healer:
        os.environ["BLOG_AI_ENABLED"] = "true"
    if args.ai_gen_data:
        os.environ["BLOG_AI_GEN_DATA"] = "true"
    if args.ai_healer:
        os.environ["BLOG_AI_HEALER"] = "true"


if __name__ == "__main__":
    args = parse_args()
    apply_runtime_args(args)

    from common.ai import analyze_result_failures, summarize_result, write_summary_file
    from common.logger import get_logger, init_logging
    from common.report import ReportTextRunner, generate_html_report, now
    from tests.runtest import build_suite

    init_logging()
    logger = get_logger("runner")
    started_at = now()
    logger.info("开始执行博客系统 UI 自动化测试")

    runner = ReportTextRunner(verbosity=2)
    result = runner.run(build_suite())
    ended_at = now()

    analyses = {}
    summary = None
    try:
        analyses = analyze_result_failures(result)
        summary = summarize_result(result, started_at, ended_at, analyses=analyses)
        write_summary_file(summary, ended_at=ended_at)
    except Exception as exc:
        logger.warning("AI 后处理失败，已跳过: %s", exc)

    report_file = generate_html_report(
        result,
        started_at,
        ended_at,
        analyses=analyses,
        summary=summary,
    )
    logger.info("测试执行结束，报告生成位置: %s", report_file)
    raise SystemExit(0 if result.wasSuccessful() else 1)
