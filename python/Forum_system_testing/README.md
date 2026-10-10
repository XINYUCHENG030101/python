# 博客系统 UI 自动化

基于 `selenium + unittest + Page Object` 的 UI 自动化测试项目，覆盖博客系统的登录、未登录拦截、列表、写博客、编辑删除和详情页。对外就用这个名称。磁盘目录仍是 `Forum_system_testing`，下面的命令路径按这个目录来。

被测地址：`http://115.190.63.202:9090/blog_login.html`

## 目录结构

```text
Forum_system_testing/   # 磁盘目录。对外名称是「博客系统 UI 自动化」
|-- config/          # 配置层
|-- common/          # 公共能力：驱动、基类、日志、报告、AI
|-- pages/           # 页面对象层
|-- tests/           # 测试用例层
|-- .env.example     # 环境变量示例
|-- requirements.txt # 依赖清单
|-- run.py           # 统一运行入口
```

## 覆盖范围

- `login`：正确账号登录成功并写入 token；错误密码、用户不存在、账号或密码为空；未登录访问列表、详情、更新页会回到登录页；写博客页打开时可停留，提交才会被拦回登录；注销后再次访问列表需要登录
- `list`：每篇博客都有标题、`yyyy-MM-dd HH:mm` 日期、摘要和详情链接；左侧用户名为当前账号，GitHub 链接为 https 地址；导航进入写博客页且按钮文案为「发布文章」
- `edit`：发布一篇带时间戳的博客并校验列表正文；另有一条在编辑框里逐字输入后再发布。再编辑标题和正文，确认创建时间不变，最后删除并确认列表中消失。另有一条在更新页用逐字输入改正文后再提交；空标题或空正文发布会被拒绝且列表不变；删除时取消确认则文章仍在。用例结束会清理自己创建的文章
- `details`：详情地址、标题、日期、正文片段、作者和 GitHub 与列表一致，作者本人能看到编辑和删除，返回后首篇标题不变；无效 blogId 会提示内部错误且内容区为空

## 环境准备

1. 创建环境变量文件

```powershell
copy .env.example .env
```

2. 安装依赖

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
```

## 运行方式

在项目根目录执行，并设置 `PYTHONPATH`：

```powershell
$env:PYTHONPATH='C:\Users\User\Desktop\github\python\Forum_system_testing'
& .\.venv\Scripts\python.exe .\run.py
```

只跑登录套件：

```powershell
$env:PYTHONPATH='C:\Users\User\Desktop\github\python\Forum_system_testing'
& .\.venv\Scripts\python.exe .\run.py --suite login
```

指定地址并启用无头模式：

```powershell
$env:PYTHONPATH='C:\Users\User\Desktop\github\python\Forum_system_testing'
& .\.venv\Scripts\python.exe .\run.py --suite all --base-url http://115.190.63.202:9090 --headless
```

## 输出产物

- 失败截图输出到 `images/`
- 运行日志输出到 `logs/`
- HTML 报告输出到 `reports/`
- 若启用 AI：失败分析在 `reports/ai_failures/`，摘要在 `reports/ai_summary_*.md`，并写入 HTML 报告

## AI 能力（可选，默认关闭）

已落地 **P0 失败归因 / P1 报告摘要 / P2 测试数据 / P3 定位建议**。方案见 `docs/AI_INTEGRATION.md`。

```text
BLOG_AI_ENABLED=true
BLOG_AI_BASE_URL=https://api.openai.com/v1
BLOG_AI_API_KEY=你的密钥
BLOG_AI_MODEL=gpt-4o-mini
BLOG_AI_GEN_DATA=false
BLOG_AI_HEALER=false
```

```powershell
$env:PYTHONPATH='C:\Users\User\Desktop\github\python\Forum_system_testing'
# 失败分析 + 摘要
& .\.venv\Scripts\python.exe .\run.py --suite login --headless --ai
# edit 套件用 AI 生成标题/正文
& .\.venv\Scripts\python.exe .\run.py --suite edit --headless --ai-gen-data
# 定位器临时自愈（演示用，正式回归建议关闭）
& .\.venv\Scripts\python.exe .\run.py --suite login --headless --ai-healer
```

未配置 Key 或 AI 调用失败时，测试结果不受影响，仅降级跳过。

## 扩展方式

### 新增页面

1. 在 `pages/` 下新增页面对象
2. 将元素定位和页面操作封装成方法

### 新增用例

1. 在 `tests/` 下新增测试类
2. 继承 `common.base_case.BaseCase`
3. 在 `tests/runtest.py` 中注册测试套件

## 注意事项

- 默认浏览器为 Chrome
- 默认账号为 `zhangsan` / `123456`
- 执行前请确保博客系统可访问
- `edit` 套件会发布带时间戳的文章，并在用例结束时删掉自己创建的那几篇
