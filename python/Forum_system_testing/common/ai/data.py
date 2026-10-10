import json
import re

from common.ai import client, prompts
from common.logger import get_logger
from config import settings

logger = get_logger("ai.data")

_TITLE_PREFIX = "自动化测试"
_FORBIDDEN = re.compile(
    r"(?i)(https?://|password|passwd|token|api[_-]?key|javascript:|<script)"
)


def _extract_json(text):
    raw = (text or "").strip()
    if not raw:
        return None
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None


def _validate_payload(title, content, stamp, title_prefix, max_len=None):
    title = (title or "").strip()
    content = (content or "").replace("\r\n", "\n").strip()
    content = " ".join(content.split())
    max_len = max_len if max_len is not None else settings.AI_DATA_CONTENT_MAX

    if not title or not content:
        return None, "标题或正文为空"
    if stamp not in title:
        return None, "标题未包含时间戳"
    if not title.startswith(title_prefix):
        return None, f"标题未以 {title_prefix} 开头"
    if len(title) > 80:
        return None, "标题过长"
    if len(content) > max_len:
        content = content[:max_len].rstrip()
    if len(content) < 4:
        return None, "正文过短"
    if _FORBIDDEN.search(title) or _FORBIDDEN.search(content):
        return None, "包含禁用内容"
    if "\n" in content:
        return None, "正文必须是单行"
    return {"title": title, "content": content}, None


def _content_limit(purpose):
    limit = settings.AI_DATA_CONTENT_MAX
    if "typing" in (purpose or ""):
        return min(limit, 40)
    return limit


def generate_blog_payload(stamp, title_prefix=None, purpose="publish"):
    """Ask the model for title/content. Returns dict or None (caller should fallback)."""
    if not client.is_enabled() or not settings.AI_GEN_DATA:
        return None

    prefix = title_prefix or _TITLE_PREFIX
    max_content = _content_limit(purpose)
    messages = [
        {"role": "system", "content": prompts.DATA_SYSTEM},
        {
            "role": "user",
            "content": prompts.data_user_prompt(
                stamp=stamp,
                title_prefix=prefix,
                purpose=purpose,
                max_content=max_content,
            ),
        },
    ]
    raw = client.chat(messages)
    data = _extract_json(raw)
    if not isinstance(data, dict):
        logger.warning("AI 测试数据解析失败，回退本地数据")
        return None

    payload, reason = _validate_payload(
        data.get("title"),
        data.get("content"),
        stamp=stamp,
        title_prefix=prefix,
        max_len=max_content,
    )
    if not payload:
        logger.warning("AI 测试数据校验失败（%s），回退本地数据", reason)
        return None

    logger.info("已使用 AI 生成博客数据: %s", payload["title"])
    return payload


def blog_payload(stamp, title_prefix="自动化测试", content_prefix="自动化正文", purpose="publish"):
    """Return AI payload when enabled, otherwise deterministic local data."""
    generated = generate_blog_payload(stamp, title_prefix=title_prefix, purpose=purpose)
    if generated:
        return generated
    return {
        "title": f"{title_prefix}-{stamp}",
        "content": f"{content_prefix}-{stamp}",
    }
