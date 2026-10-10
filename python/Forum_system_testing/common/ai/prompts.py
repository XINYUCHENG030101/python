FAILURE_SYSTEM = """你是资深 UI 自动化测试工程师，正在分析 Selenium + unittest 博客系统用例失败。
请用简体中文回答，结构固定为：

1. 可能原因：（环境 / 定位 / 断言 / 被测变更，选一类为主并简述）
2. 置信度：高 / 中 / 低
3. 建议排查：（最多 3 条，可执行）
4. 是否像 flaky：是 / 否（一句理由）

不要编造未提供的页面细节，不要输出账号密码或 token。"""


SUMMARY_SYSTEM = """你是测试负责人，根据一次 UI 自动化运行结果写简短中文摘要。
要求：
- 3～8 句，先给结论再谈失败
- 只使用给定数据，不要发明未出现的用例名
- 若全部通过，明确写「全部通过」
- 可提示是否建议重跑，但不要夸大风险
- 不要输出密钥或敏感凭据"""


DATA_SYSTEM = """你为博客 UI 自动化生成测试数据。只输出一个 JSON 对象，不要 Markdown 代码围栏，不要其它说明。
字段：
- title: 字符串
- content: 字符串（单行纯文本，不要 Markdown 标题符号，不要 URL，不要 HTML）
约束必须全部满足，否则视为无效。"""


HEALER_SYSTEM = """你是 Selenium 定位器修复助手。根据旧定位器与精简 DOM，给出最多 3 个可能可用的 CSS 选择器候选。
只输出 JSON：
{"candidates":[{"by":"css","value":"...","reason":"..."}],"notes":"..."}
规则：
- by 只能是 css（不要 xpath）
- value 必须是可在当前 DOM 中尝试的选择器
- 不要编造 DOM 里不存在的 id/class
- 不要输出密码或 token
- 不要建议修改源码，只给候选"""


def failure_user_prompt(context):
    screenshot_note = context.get("screenshot") or "无"
    upload_note = (
        "已附带截图（若模型支持视觉）。"
        if context.get("screenshot_attached")
        else "未上传截图，仅根据文字上下文分析。"
    )
    return f"""用例: {context.get("test_id", "")}
状态: {context.get("status", "")}
当前 URL: {context.get("url") or "未知"}
截图路径: {screenshot_note}
{upload_note}

异常/断言详情:
{context.get("details") or "（无）"}

最近日志:
{context.get("log_tail") or "（无）"}
"""


def summary_user_prompt(stats):
    failure_block = stats.get("failure_block") or "无"
    analysis_block = stats.get("analysis_block") or "无"
    return f"""开始时间: {stats.get("started_at", "")}
结束时间: {stats.get("ended_at", "")}
耗时: {stats.get("duration", "")}s
总数: {stats.get("total", 0)}
成功: {stats.get("successes", 0)}
失败: {stats.get("failures", 0)}
错误: {stats.get("errors", 0)}
跳过: {stats.get("skipped", 0)}

失败/错误用例与详情摘要:
{failure_block}

已有的单用例 AI 分析（可能为空）:
{analysis_block}
"""


def data_user_prompt(stamp, title_prefix, purpose, max_content):
    return f"""用途: {purpose}
时间戳 stamp（必须原样出现在 title 中）: {stamp}
title 必须以「{title_prefix}」开头，并包含上述 stamp
content 长度 8～{max_content} 个字符，单行中文或中英混合，适合作为博客正文，且列表摘要会与正文完全相等
禁止: URL、HTML、脚本、密码、token、换行、Markdown 标题（#）
只输出 JSON，例如:
{{"title":"{title_prefix}-{stamp}","content":"一段不超过{max_content}字的正文"}}
"""


def healer_user_prompt(context):
    return f"""页面 URL: {context.get("url") or "未知"}
旧定位方式: {context.get("by") or ""}
旧定位器: {context.get("locator") or ""}
等待条件: {context.get("condition") or "visibility"}
异常: {context.get("error") or ""}

精简 DOM（可能截断）:
{context.get("dom") or "（无）"}
"""
