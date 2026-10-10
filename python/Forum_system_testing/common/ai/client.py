import base64
from pathlib import Path

import requests

from common.logger import get_logger
from config import settings

logger = get_logger("ai.client")


def is_enabled():
    return bool(settings.AI_ENABLED and settings.AI_API_KEY)


def chat(messages, timeout=None):
    """Call an OpenAI-compatible chat completions API. Returns text or None."""
    if not is_enabled():
        return None

    url = f"{settings.AI_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.AI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.AI_MODEL,
        "messages": messages,
        "temperature": 0.2,
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=timeout or settings.AI_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            logger.warning("AI 响应缺少 choices: %s", data)
            return None
        message = choices[0].get("message") or {}
        content = message.get("content")
        if not content:
            logger.warning("AI 响应内容为空")
            return None
        return str(content).strip()
    except Exception as exc:
        logger.warning("AI 调用失败，已降级跳过: %s", exc)
        return None


def image_data_url(path):
    """Build a data URL for vision-capable models. Returns None on failure."""
    file_path = Path(path) if path else None
    if not file_path or not file_path.is_file():
        return None
    try:
        raw = file_path.read_bytes()
        encoded = base64.b64encode(raw).decode("ascii")
        suffix = file_path.suffix.lower().lstrip(".") or "png"
        mime = "image/jpeg" if suffix in {"jpg", "jpeg"} else f"image/{suffix}"
        return f"data:{mime};base64,{encoded}"
    except Exception as exc:
        logger.warning("读取截图失败，跳过上传: %s", exc)
        return None
