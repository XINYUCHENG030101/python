# 博客系统 UI 自动化 · AI 能力接入方案

本文档描述如何在现有 `selenium + unittest + Page Object` 框架上分阶段接入 AI，**只定方向与步骤，不要求一次性改完**。  
对外项目名：「博客系统 UI 自动化」。磁盘目录仍为 `Forum_system_testing`。

相关背景见根目录 `README.md`。

---

## 1. 目标与原则

### 1.1 目标

在不破坏现有约 16 条稳定用例的前提下，用 AI 增强：

1. 失败归因（截图 + 日志 + 异常）
2. 全量报告中文摘要
3. 可选的测试数据生成（博客标题 / Markdown 正文）
4. 可选的定位器修复建议（默认不自动改代码）

### 1.2 原则

| 原则 | 说明 |
|------|------|
| 旁路增强 | AI 挂在执行链路旁，不替换 Page Object 与核心断言 |
| 默认关闭 | `BLOG_AI_ENABLED=false` 时行为与现在完全一致 |
| 失败降级 | AI 调用失败只记 warning，不把整场测试标成 ERROR |
| 密钥外置 | API Key 只放 `.env`，不进仓库 |
| 线上安全 | `edit` 套件若用 AI 生成正文，仍必须走时间戳标题 + 用例结束清理 |

---

## 2. 建议目录结构

落地后建议新增（名称可微调，层级保持清晰即可）：

```text
Forum_system_testing/
|-- common/
|   `-- ai/
|       |-- __init__.py
|       |-- client.py       # 统一调模型：超时、重试、开关
|       |-- prompts.py      # 各场景提示词模板
|       |-- failure.py      # 失败归因：组装上下文 → 分析结果
|       |-- summarize.py    # 报告摘要
|       |-- data.py         # 测试数据生成（P2）
|       `-- healer.py       # 定位器建议（P3，默认关闭）
|-- docs/
|   `-- AI_INTEGRATION.md   # 本文档
|-- config/settings.py      # 增加 BLOG_AI_* 配置项
|-- .env.example            # 补充 AI 相关变量示例
```

依赖建议（按阶段追加，不必一次装全）：

```text
# P0 起
openai>=1.0.0          # 或任意 OpenAI 兼容 SDK；也可用 requests 直调 HTTP
Pillow>=10.0.0         # 可选：压缩截图再上传，控制 token
```

若团队统一用国内中转 / Ollama，只需在 `client.py` 里换 `base_url` 与模型名，业务模块不必改。

---

## 3. 配置项设计

在 `.env.example` / `.env` 与 `config/settings.py` 中预留：

```text
BLOG_AI_ENABLED=false
BLOG_AI_BASE_URL=https://api.openai.com/v1
BLOG_AI_API_KEY=
BLOG_AI_MODEL=gpt-4o-mini
BLOG_AI_TIMEOUT=60
BLOG_AI_FAILURE_ANALYSIS=true
BLOG_AI_REPORT_SUMMARY=true
BLOG_AI_GEN_DATA=false
BLOG_AI_HEALER=false
BLOG_AI_UPLOAD_SCREENSHOT=false
```

说明：

- `BLOG_AI_ENABLED`：总开关；为 false 时其余 AI 逻辑直接 no-op。
- `BLOG_AI_UPLOAD_SCREENSHOT`：是否把截图发给云端模型；关闭时仅用文字上下文（栈、日志、URL），更安全。
- 密钥变量不要写入 HTML 报告或日志明文。

---

## 4. 分阶段步骤

### P0 · 失败智能归因（优先）

**目标**：用例失败后自动产出中文排查说明，写入报告或独立文件。

#### 步骤

1. **新建 `common/ai/client.py`**
   - 读取 `settings` 中的 AI 配置。
   - 封装 `chat(messages, **kwargs) -> str`。
   - 未启用 / 无 Key / 超时：返回空或抛出自定义可捕获异常，由上层降级。

2. **新建 `common/ai/prompts.py`**
   - 定义失败分析 system / user 模板，要求模型输出固定结构，例如：
     - 可能原因（环境 / 定位 / 断言 / 被测变更）
     - 置信度（高 / 中 / 低）
     - 建议排查步骤（3 条以内）
     - 是否像 flaky

3. **新建 `common/ai/failure.py`**
   - 输入：用例 id、异常文本、当前 URL、截图路径、最近 N 行日志、相关 Page 类名（可选）。
   - 脱敏：去掉密码、token、完整 API Key。
   - 调用 `client.chat`，返回结构化文本或简单 dict。

4. **挂接点（二选一或都做）**
   - **A.** 在 `common/base_case.py` 的 `save_failure_screenshot` 之后调用 `failure.analyze(...)`，结果写到 `reports/ai_failures/` 或挂到 test 对象属性上。
   - **B.** 在 `run.py` 跑完后遍历 `result.failures` / `result.errors`，批量分析（更集中，少改用例基类）。

5. **报告展示**
   - 扩展 `common/report.py`：失败行增加「AI 分析」列或折叠区块；无分析结果时显示「未启用 / 分析跳过」。

6. **验收**
   - `BLOG_AI_ENABLED=false`：全量仍 16 通过，报告无 AI 区块或显示跳过。
   - 人为改坏一个定位器再跑：失败用例旁出现可读的中文归因。
   - 关掉网络或错误 Key：测试结果本身不变，仅日志 warning。

---

### P1 · 全量报告中文摘要

**目标**：一次 `--suite all` 结束后，得到一段给测试/开发看的摘要。

#### 步骤

1. **新建 `common/ai/summarize.py`**
   - 输入：总数、成功/失败/错误/跳过、失败用例 id 列表、各失败详情摘要、耗时。
   - 输出：3～8 句中文：整体结论、失败聚类、是否建议重跑、风险提示。

2. **挂接 `run.py`**
   - 在 `generate_html_report(...)` 之后（或之内）调用摘要。
   - 将摘要写入 HTML 顶部，并可选另存 `reports/ai_summary_YYYYMMDD_HHMMSS.md`。

3. **验收**
   - 全绿时摘要应明确「全部通过」且不胡编失败原因。
   - 有失败时摘要与报告表格一致，不出现未跑过的用例名。

---

### P2 · AI 测试数据生成

**目标**：为发布/编辑类用例提供更丰富、仍可清理的正文数据。

#### 步骤

1. **新建 `common/ai/data.py`**
   - `generate_blog_payload()` → `{title, content}`。
   - **硬约束**（提示词 + 本地校验双保险）：
     - 标题必须含可识别时间戳或统一前缀（与现有清理策略兼容）。
     - 正文为合法 Markdown 纯文本，长度上限（如 2KB）。
     - 禁止生成账号密码、外链钓鱼内容等。

2. **改造用例侧（保持可选）**
   - 在 `tests/Blog_edit.py` 增加开关：`BLOG_AI_GEN_DATA=true` 时用 AI 数据，否则仍用现有固定/时间戳字符串。
   - 继续调用 `pages` 已有方法（`publish_*` / `type_markdown`），**不要**让模型直接操作 WebDriver。

3. **清理**
   - 复用 `tests/support.py` 的 `delete_titles`，确保只删本用例创建的标题。

4. **验收**
   - 开关关闭：与现有 edit 套件行为一致。
   - 开关打开：发布成功、列表摘要匹配、tearDown 后线上不残留 AI 文章。

---

### P3 · 定位器自愈建议（谨慎）

**目标**：元素找不到时给出「可能的新定位器」，供人工确认；默认不自动写回代码。

#### 步骤

1. **新建 `common/ai/healer.py`**
   - 输入：旧定位器、异常信息、当前页精简 DOM（截断 + 去 script）、页面语义描述。
   - 输出：候选 CSS/XPath 列表 + 理由。

2. **挂接 `common/base_page.py`（仅当 `BLOG_AI_HEALER=true`）**
   - `find` / `click` 捕获超时后调用 healer。
   - 对每个候选做一次「存在且可见」校验；成功则**本用例内临时使用**，并写 `logs/` 建议记录。
   - **禁止**默认自动改 `pages/*.py` 源码。

3. **人工闭环**
   - 从日志/报告复制建议 → 开发改 Page Object → 再跑套件确认。

4. **验收**
   - 默认关闭时零行为变化。
   - 开启时：错误定位器场景下日志出现候选，且不会因 AI 失败导致驱动崩溃。

---

## 5. 推荐挂接顺序（实现时对照）

```text
run.py
  └─ build_suite() / runner.run()
        └─ BaseCase
              └─ 失败 → 截图 → [P0] failure.analyze
  └─ generate_html_report
        └─ [P0] 嵌入失败分析
        └─ [P1] summarize → 写摘要
  └─ [P2] 用例内部按需 generate_blog_payload
  └─ [P3] BasePage.find 超时 → healer（默认关）
```

---

## 6. 安全与合规清单

实施每一阶段前核对：

- [ ] `.env` 在 `.gitignore` 中，Key 未进提交
- [ ] 日志/报告中无完整 token、密码
- [ ] 默认不上传截图到公网；若上传，已评估页面是否含敏感信息
- [ ] AI 生成的文章标题可被现有清理逻辑删除
- [ ] CI（若后续接入）用仓库 Secrets 注入 Key，且 AI 失败不阻断必要门禁（或单独 job）

---

## 7. 验收总表

| 阶段 | 最小验收标准 |
|------|----------------|
| P0 | 总开关关闭无差异；开启后失败用例有中文归因；AI 宕机不影响判定 |
| P1 | 报告顶部有与结果一致的中文摘要 |
| P2 | 可选生成数据发布并清理干净 |
| P3 | 仅建议+临时代用，不自动改仓库；默认关闭 |

---

## 8. 工作量粗估（供排期）

| 阶段 | 建议工期 | 依赖 |
|------|----------|------|
| P0 | 1～2 天 | 可用的模型 API |
| P1 | 0.5～1 天 | 依赖 P0 的 client |
| P2 | 1 天 | 依赖 client；熟悉 edit 清理逻辑 |
| P3 | 2～3 天 | DOM 截断与误报控制，需多轮试 |

同机接口项目 `Auto_test/apitest` 若也要接 AI，**复用同一套 client 配置约定**，避免两套 Key 与提示词分叉。

---

## 9. 明确不做（本阶段）

- 不用 AI 替换现有硬编码断言作为唯一判据
- 不在无人工确认时自动提交/修改 `pages/` 定位器
- 不把「让模型写完整 Selenium 脚本并直接打线上」当作主路径
- 不做自然语言 → 用例草稿（原 P4 已移除）
- 不在本文档阶段改被测博客业务系统本身

---

## 10. 实现进度

| 阶段 | 状态 | 说明 |
|------|------|------|
| P0 失败归因 | **已完成** | `failure.py`；`reports/ai_failures/` + HTML「AI 分析」 |
| P1 报告摘要 | **已完成** | `summarize.py`；`reports/ai_summary_*.md` + HTML「AI 摘要」 |
| P2 测试数据 | **已完成** | `data.py` + `Blog_edit` 的 `blog_payload`；`--ai-gen-data`；edit 7/7 开关关/开均过 |
| P3 定位器建议 | **已完成** | `healer.py` + `BasePage._wait_element`；`--ai-healer`；默认关，不改源码 |

启用方式：`.env` 的 `BLOG_AI_*`，或 `run.py --ai` / `--ai-gen-data` / `--ai-healer`。无 Key 时全链路降级。

## 11. 下一步

1. 日常回归保持 `BLOG_AI_HEALER=false`。
2. 可选：把 healer 建议汇总进 HTML「人工确认清单」。
3. 可选：全量 `--suite all --headless`（AI 全关）做一次无回归确认。
