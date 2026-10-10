from datetime import datetime

from common.ai import client, prompts
from common.logger import get_logger
from config import settings

logger = get_logger("ai.summarize")


def _clip(text, limit=800):
    value = (text or "").strip()
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."


def _failure_block(result):
    lines = []
    for status, entries in (("FAIL", result.failures), ("ERROR", result.errors)):
        for test_case, details in entries:
            lines.append(f"- [{status}] {test_case.id()}")
            lines.append(f"  {_clip(details, 500)}")
    return "\n".join(lines) if lines else "无"


def _analysis_block(analyses):
    if not analyses:
        return "无"
    lines = []
    for test_id, text in analyses.items():
        lines.append(f"- {test_id}")
        lines.append(f"  {_clip(text, 600)}")
    return "\n".join(lines)


def summarize_result(result, started_at, ended_at, analyses=None):
    if not client.is_enabled() or not settings.AI_REPORT_SUMMARY:
        logger.info("AI 报告摘要未启用，跳过")
        return None

    duration = (ended_at - started_at).total_seconds()
    stats = {
        "started_at": started_at.strftime("%Y-%m-%d %H:%M:%S"),
        "ended_at": ended_at.strftime("%Y-%m-%d %H:%M:%S"),
        "duration": f"{duration:.2f}",
        "total": result.testsRun,
        "successes": len(result.successes),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "failure_block": _failure_block(result),
        "analysis_block": _analysis_block(analyses or {}),
    }
    messages = [
        {"role": "system", "content": prompts.SUMMARY_SYSTEM},
        {"role": "user", "content": prompts.summary_user_prompt(stats)},
    ]
    summary = client.chat(messages)
    if summary:
        logger.info("AI 报告摘要已生成")
    return summary


def write_summary_file(summary, ended_at=None):
    if not summary:
        return None
    settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = (ended_at or datetime.now()).strftime("%Y%m%d_%H%M%S")
    path = settings.REPORTS_DIR / f"ai_summary_{stamp}.md"
    path.write_text(f"# AI 测试报告摘要\n\n{summary}\n", encoding="utf-8")
    logger.info("已写入 AI 摘要: %s", path)
    return path
