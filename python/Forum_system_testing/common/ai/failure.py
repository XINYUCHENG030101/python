import re

from common.ai import client, prompts
from common.logger import get_logger
from config import settings

logger = get_logger("ai.failure")

_SECRET_PATTERNS = (
    (re.compile(r"(?i)(api[_-]?key|token|password|passwd|secret)\s*[:=]\s*\S+"), r"\1=[REDACTED]"),
    (re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*"), "Bearer [REDACTED]"),
    (re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"), "[JWT_REDACTED]"),
)


def _redact(text):
    value = text or ""
    for pattern, replacement in _SECRET_PATTERNS:
        value = pattern.sub(replacement, value)
    if settings.PASSWORD:
        value = value.replace(settings.PASSWORD, "[REDACTED]")
    if settings.WRONG_PASSWORD:
        value = value.replace(settings.WRONG_PASSWORD, "[REDACTED]")
    if settings.AI_API_KEY:
        value = value.replace(settings.AI_API_KEY, "[REDACTED]")
    return value


def _read_log_tail(max_lines=None):
    log_file = settings.LOG_FILE
    if not log_file.is_file():
        return ""
    try:
        lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
        limit = max_lines or settings.AI_LOG_TAIL_LINES
        return "\n".join(lines[-limit:])
    except Exception as exc:
        logger.warning("读取日志尾部失败: %s", exc)
        return ""


def _failure_context(test_case):
    context = getattr(test_case, "_failure_context", None) or {}
    return {
        "screenshot": context.get("screenshot"),
        "url": context.get("url"),
    }


def _write_analysis_file(test_id, analysis):
    settings.AI_FAILURES_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^\w.\-]+", "_", test_id)
    path = settings.AI_FAILURES_DIR / f"{safe_name}.md"
    path.write_text(
        f"# AI 失败分析\n\n用例: `{test_id}`\n\n{analysis}\n",
        encoding="utf-8",
    )
    return path


def analyze_failure(test_id, status, details, screenshot=None, url=None):
    if not client.is_enabled() or not settings.AI_FAILURE_ANALYSIS:
        return None

    context = {
        "test_id": test_id,
        "status": status,
        "details": _redact(details),
        "screenshot": screenshot or "",
        "url": url or "",
        "log_tail": _redact(_read_log_tail()),
        "screenshot_attached": False,
    }

    user_content = prompts.failure_user_prompt(context)
    messages = [
        {"role": "system", "content": prompts.FAILURE_SYSTEM},
        {"role": "user", "content": user_content},
    ]

    if settings.AI_UPLOAD_SCREENSHOT and screenshot:
        data_url = client.image_data_url(screenshot)
        if data_url:
            context["screenshot_attached"] = True
            messages[1] = {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompts.failure_user_prompt(context)},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }

    analysis = client.chat(messages)
    if not analysis:
        return None

    try:
        path = _write_analysis_file(test_id, analysis)
        logger.info("已写入 AI 失败分析: %s", path)
    except Exception as exc:
        logger.warning("写入 AI 失败分析文件失败: %s", exc)
    return analysis


def analyze_result_failures(result):
    """Analyze FAIL/ERROR cases. Returns {test_id: analysis_text}."""
    analyses = {}
    if not client.is_enabled() or not settings.AI_FAILURE_ANALYSIS:
        logger.info("AI 失败分析未启用，跳过")
        return analyses

    batches = (
        ("FAIL", result.failures),
        ("ERROR", result.errors),
    )
    for status, entries in batches:
        for test_case, details in entries:
            test_id = test_case.id()
            ctx = _failure_context(test_case)
            analysis = analyze_failure(
                test_id=test_id,
                status=status,
                details=details,
                screenshot=ctx.get("screenshot"),
                url=ctx.get("url"),
            )
            if analysis:
                analyses[test_id] = analysis
                try:
                    test_case._ai_analysis = analysis
                except Exception:
                    pass
    return analyses
