import json
import re
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from common.ai import client, prompts
from common.logger import get_logger
from config import settings

logger = get_logger("ai.healer")

_SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script>", re.I | re.S)
_STYLE_RE = re.compile(r"<style\b[^>]*>.*?</style>", re.I | re.S)


def is_enabled():
    return bool(client.is_enabled() and settings.AI_HEALER)


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


def simplify_dom(page_source, limit=None):
    html = page_source or ""
    html = _SCRIPT_RE.sub("", html)
    html = _STYLE_RE.sub("", html)
    html = re.sub(r"\s+", " ", html)
    max_chars = limit or settings.AI_HEALER_DOM_CHARS
    if len(html) > max_chars:
        html = html[:max_chars] + " <!-- truncated -->"
    return html


def suggest_locators(driver, by, locator, condition="visibility", error=""):
    if not is_enabled():
        return []

    try:
        url = driver.current_url
        dom = simplify_dom(driver.page_source)
    except Exception as exc:
        logger.warning("采集 DOM 失败，跳过自愈建议: %s", exc)
        return []

    context = {
        "url": url,
        "by": by,
        "locator": locator,
        "condition": condition,
        "error": str(error),
        "dom": dom,
    }
    messages = [
        {"role": "system", "content": prompts.HEALER_SYSTEM},
        {"role": "user", "content": prompts.healer_user_prompt(context)},
    ]
    raw = client.chat(messages)
    data = _extract_json(raw) or {}
    candidates = []
    for item in data.get("candidates") or []:
        if not isinstance(item, dict):
            continue
        value = (item.get("value") or "").strip()
        if not value:
            continue
        by_name = (item.get("by") or "css").strip().lower()
        if by_name not in {"css", "css selector", "css_selector"}:
            continue
        candidates.append(
            {
                "by": By.CSS_SELECTOR,
                "value": value,
                "reason": (item.get("reason") or "").strip(),
            }
        )
    _write_suggestion_file(context, candidates, data.get("notes") or "", raw or "")
    return candidates[:3]


def _write_suggestion_file(context, candidates, notes, raw):
    settings.AI_HEALER_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = settings.AI_HEALER_DIR / f"suggest_{stamp}.md"
    lines = [
        "# AI 定位器建议",
        "",
        f"- URL: `{context.get('url')}`",
        f"- 旧定位: `{context.get('by')}` / `{context.get('locator')}`",
        f"- 条件: `{context.get('condition')}`",
        "",
        "## 候选",
        "",
    ]
    if not candidates:
        lines.append("（无有效候选）")
    for idx, item in enumerate(candidates, 1):
        lines.append(f"{idx}. `{item['value']}` — {item.get('reason') or '无说明'}")
    lines.extend(["", "## 备注", "", notes or "无", "", "## 原始响应", "", "```", raw[:4000], "```", ""])
    try:
        path.write_text("\n".join(lines), encoding="utf-8")
        logger.info("已写入定位器建议: %s", path)
    except Exception as exc:
        logger.warning("写入定位器建议失败: %s", exc)


def try_heal(driver, by, locator, condition="visibility", error=""):
    """Try AI candidates. Returns WebElement on success, else None. Never edits source."""
    if not is_enabled():
        return None

    candidates = suggest_locators(
        driver, by=by, locator=locator, condition=condition, error=error
    )
    if not candidates:
        logger.warning("定位器自愈无候选: %s", locator)
        return None

    short_wait = WebDriverWait(driver, min(3, settings.EXPLICIT_WAIT))
    for item in candidates:
        try:
            if condition == "clickable":
                element = short_wait.until(
                    EC.element_to_be_clickable((item["by"], item["value"]))
                )
            else:
                element = short_wait.until(
                    EC.visibility_of_element_located((item["by"], item["value"]))
                )
            logger.warning(
                "定位器临时自愈成功（仅本调用）: %s -> %s （%s）",
                locator,
                item["value"],
                item.get("reason") or "无说明",
            )
            return element
        except Exception:
            continue

    logger.warning("定位器自愈候选均未命中: %s", locator)
    return None
