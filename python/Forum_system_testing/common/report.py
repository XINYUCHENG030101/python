import datetime
import html
import unittest

from config import settings


class ReportTextResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.successes = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.successes.append(test)


class ReportTextRunner(unittest.TextTestRunner):
    resultclass = ReportTextResult


def _build_case_rows(items, status, analyses=None, details_getter=None):
    analyses = analyses or {}
    rows = []
    for entry in items:
        if isinstance(entry, tuple):
            test_case = entry[0]
            details = entry[1]
        else:
            test_case = entry
            details = ""

        details_text = details_getter(details) if details_getter else details
        test_id = test_case.id()
        ai_text = analyses.get(test_id) or getattr(test_case, "_ai_analysis", "") or ""
        if status in {"FAIL", "ERROR"} and not ai_text:
            ai_text = "未启用或分析跳过"
        elif status not in {"FAIL", "ERROR"}:
            ai_text = "-"

        rows.append(
            "<tr>"
            f"<td>{html.escape(test_id)}</td>"
            f"<td>{status}</td>"
            f"<td><pre>{html.escape(details_text)}</pre></td>"
            f"<td><pre>{html.escape(ai_text)}</pre></td>"
            "</tr>"
        )
    return rows


def generate_html_report(result, started_at, ended_at, analyses=None, summary=None):
    settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    duration = (ended_at - started_at).total_seconds()
    analyses = analyses or {}
    rows = []
    rows.extend(_build_case_rows(result.successes, "PASS", analyses))
    rows.extend(_build_case_rows(result.failures, "FAIL", analyses))
    rows.extend(_build_case_rows(result.errors, "ERROR", analyses))
    rows.extend(_build_case_rows(result.skipped, "SKIP", analyses))

    summary_html = ""
    if summary:
        summary_html = (
            "<h2>AI 摘要</h2>"
            f"<pre class=\"ai-summary\">{html.escape(summary)}</pre>"
        )

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>UI 自动化测试报告</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
    th {{ background: #f4f4f4; }}
    .summary span {{ margin-right: 16px; }}
    pre {{ white-space: pre-wrap; word-break: break-word; margin: 0; }}
    .ai-summary {{ background: #f9fafb; border: 1px solid #eee; padding: 12px; }}
  </style>
</head>
<body>
  <h1>UI 自动化测试报告</h1>
  <div class="summary">
    <span>开始时间: {started_at.strftime("%Y-%m-%d %H:%M:%S")}</span>
    <span>结束时间: {ended_at.strftime("%Y-%m-%d %H:%M:%S")}</span>
    <span>耗时: {duration:.2f}s</span>
    <span>总数: {result.testsRun}</span>
    <span>成功: {len(result.successes)}</span>
    <span>失败: {len(result.failures)}</span>
    <span>错误: {len(result.errors)}</span>
    <span>跳过: {len(result.skipped)}</span>
  </div>
  {summary_html}
  <table>
    <thead>
      <tr>
        <th>用例</th>
        <th>结果</th>
        <th>详情</th>
        <th>AI 分析</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</body>
</html>
"""

    settings.REPORT_FILE.write_text(html_content, encoding="utf-8")
    return settings.REPORT_FILE


def now():
    return datetime.datetime.now()
