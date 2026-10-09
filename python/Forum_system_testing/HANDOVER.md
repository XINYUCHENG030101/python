# 交接文档：博客系统 UI 自动化

下一窗口先读这份。这是测试项目，不是博客业务系统本身。对外名称是「博客系统 UI 自动化」。磁盘目录仍叫 `Forum_system_testing`，工作区和 `PYTHONPATH` 继续用这个路径。

## 总结

用 `selenium + unittest + Page Object` 覆盖 `http://115.190.63.202:9090` 上的比特 Spring Blog。旧论坛用例和页面对象已经删掉，环境变量前缀是 `BLOG_`。

最近一次全量：**16 条全部通过**，无头模式大约 33 秒。报告在 `reports/ui_test_report.html`。

已经覆盖：

- 登录成功、错误密码、用户不存在、账号或密码为空
- 未登录访问列表、详情、更新页会被踢回登录页；写博客页要点发布才会被拦截
- 注销后 token 清空，再进列表回到登录页
- 列表每篇的标题、日期、摘要、详情链接，以及当前用户名和 GitHub
- 发布、编辑、删除自己创建的博客，并核对正文和创建时间。发布另有一条是在编辑框里逐字输入
- 详情页标题、日期、正文、作者和返回列表

账号：`zhangsan` / `123456`。错误密码 `123`，不存在的用户 `zhangsa`。线上保留的正式文章是「博客标题」，自动化文章用时间戳标题，跑完会删掉。

## 这轮做了什么

在上一轮已经覆盖登录、未登录拦截、列表、发布、编辑删除、详情之后，把交接文档末尾留下的三件收尾做完了：

1. **删掉遗留文件。** `common/util.py` 里的旧 `Driver` 封装已经没人引用，驱动和失败截图都在 `common/base_case.py`。文件已删除。
2. **对外改名。** README 和这份交接文档对外统一叫「博客系统 UI 自动化」。磁盘目录仍是 `Forum_system_testing`，工作区和 `PYTHONPATH` 没动，避免弄断当前环境。
3. **编辑器逐字输入。** 新增 `pages/markdown_editor.py` 的 `type_markdown`，以及 `BlogEditPage.publish_typed_blog` 和用例 `test_publish_blog_by_typing`。流程是进写博客页 → 标题照常填 → 选中占位正文「##在这里写下一篇博客」→ 逐字写入新正文 → 发布 → 列表摘要等于正文 → 用例结束删掉自己这篇。

逐字输入踩过的坑已经写进下面「不要踩的坑」。单独跑新用例时 `send_keys` 还能用；跟在 `test_publish_blog` 后面、页面已经用 `location.href` 跳过一次之后，同一场浏览器里的 `send_keys` 标题框和编辑器都不进字。现在的实现是 `CodeMirror.execCommand('selectAll')`，再逐字调 Chrome CDP `Input.insertText`；第一个字替换选区，后面的字接在后面。editor.md 会稍后把内容写回隐藏的 `#content`，断言要等两边一致。原先脚本直接写入的发布、编辑用例还在。

全量已重跑：**16 条全部通过**。线上列表应只剩正式文章「博客标题」，外加当次 `edit` 套件尚未清理完的临时文章。

## 被测页面

| 页面 | 地址 | 关键元素 |
|------|------|----------|
| 登录 | `/blog_login.html` | `#username` `#password` `#submit` |
| 列表 | `/blog_list.html` | `.container .right .blog`、`.left .card h3` |
| 写博客 | `/blog_edit.html` | `#title` `#submit`（「发布文章」）`#content` |
| 详情 | `/blog_detail.html?blogId=` | `.content .title` `.content .date` `#detail` |
| 更新 | `/blog_update.html?blogId=` | `#blogId` `#title` `#submit`（「更新文章」） |

行为要点：

- 登录是 `POST /user/login`。成功把 token 写入 `localStorage.user_token` 并跳到列表。失败走 `alert(result.errMsg)`。
- `js/common.js` 给后续 AJAX 加请求头 `user_token_header`。
- 列表用户名来自 `/user/getUserInfo`。详情作者来自 `/user/getAuthorInfo`。
- 只有详情接口的 `loginUser == true` 才会插入「编辑」「删除」。列表接口里的 `loginUser` 一直是 false。
- 删除是 `confirm("确定删除?")`，然后 `POST /blog/delete?blogId=`。
- 更新提交的是编辑器里的 `#content`。列表上的日期是 `createTime`，更新后不变。
- 左侧「文章 / 分类」的数字是页面写死的，不能拿来断言。
- 同机接口项目：`C:\Users\User\Desktop\github\python\Auto_test\apitest`，打的是同一套服务。

## 代码地图

```text
Forum_system_testing/          # 磁盘目录。对外名称：博客系统 UI 自动化
|-- run.py                      # --suite / --base-url / --headless，并出 HTML 报告
|-- config/settings.py          # 读 .env，前缀 BLOG_
|-- common/
|   |-- driver_factory.py       # 优先用 .drivers 里的 chromedriver
|   |-- base_page.py            # 查找、输入、href 跳转、捕获 alert/confirm
|   |-- base_case.py            # 每个测试类一个浏览器，失败截图
|   `-- logger.py / report.py
|-- pages/
|   |-- login_page.py
|   |-- blog_list_page.py
|   |-- blog_edit_page.py
|   |-- blog_update_page.py
|   |-- blog_detail_page.py
|   `-- markdown_editor.py      # set_markdown 脚本写入；type_markdown 逐字 insertText
`-- tests/
    |-- runtest.py              # login / list / edit / details / all
    |-- support.py              # 删除本用例创建的博客
    |-- Blog_login.py           # 10 条
    |-- Blog_list.py            # 2 条
    |-- Blog_edit.py            # 3 条
    `-- Blog_details.py         # 1 条
```

## 用例一览

| 套件 | 用例 | 在断言什么 |
|------|------|------------|
| login | `test_login_success` | 进入列表，标题是「我的博客系统」，token 为三段 JWT |
| login | `test_login_fail` | 「密码错误」，停在登录页，token 为空 |
| login | `test_login_unknown_user` | 「用户不存在」 |
| login | `test_login_empty_username` / `test_login_empty_password` | 「账号或密码不能为空」 |
| login | `test_guest_list/detail/update_redirects_to_login` | 未登录打开即回到登录页 |
| login | `test_guest_editor_submit_redirects_to_login` | 未登录发布会被拦下，列表中没有该标题 |
| login | `test_logout_then_list_requires_login` | 注销后 token 为空，再进列表回到登录页 |
| list | `test_list_content` | 每篇都有标题、日期、摘要、`blogId` 链接；用户名和 GitHub 正确 |
| list | `test_open_editor_from_nav` | 写博客页按钮文案是「发布文章」 |
| edit | `test_publish_blog` | 列表摘要等于正文，随后删除 |
| edit | `test_publish_blog_by_typing` | 用按键逐字写正文，CodeMirror 和 `#content` 一致，列表摘要等于正文 |
| edit | `test_update_and_delete_own_blog` | 改标题和正文，创建时间不变，确认「确定删除?」后标题消失 |
| details | `test_blog_details_and_back_home` | 详情与列表首篇一致，作者本人能看到编辑和删除，返回后首篇仍在 |

## 环境与运行

- 工作区：`C:\Users\User\Desktop\github\python\Forum_system_testing`
- Python：`D:\python\python.exe`（3.13.15），虚拟环境用项目里的 `.venv`
- Chrome 约 **154.0.8037**，驱动在 `.drivers/chromedriver-win64/chromedriver.exe`（154.0.8037.92）
- `webdriver-manager` 对这个大版本不稳定。没有本地驱动时会落到 Selenium Manager，这台机器上可能卡住
- `.venv/`、`.drivers/`、`.env`、`images/`、`logs/`、`reports/`、`.trae/`、`.idea/` 都在 `.gitignore`
- 已删掉无用目录：旧 `.venv38`、`.trae`、`.idea`；`images/`、`logs/`、`reports/` 只保留空目录，跑测试时会重新写入

```powershell
$env:PYTHONPATH='C:\Users\User\Desktop\github\python\Forum_system_testing'
& .\.venv\Scripts\python.exe .\run.py --suite all --headless
```

单个套件：`--suite login|list|edit|details`。重装环境时复制 `.env.example`，再用 `.venv` 安装 `requirements.txt`。PyPI 不稳时可以用阿里云镜像。Chrome 大版本变了，要换匹配的 chromedriver。

## 接手时不要踩的坑

- 详情页加载 editor.md 之后，无头模式下原生 `element.click()` 有时点不到顶部链接。导航和「查看全文」走 `href`。
- 无头模式缺少用户手势时，`alert` / `confirm` 可能不弹出。登录失败和删除是先替换 `window.alert` / `window.confirm`，再断言页面准备弹出的文案。
- `#content` 是隐藏 textarea。脚本写正文要同时写入 CodeMirror，否则 editor.md 会在提交时盖掉内容。
- 逐字输入不要依赖 `send_keys`。页面自己 `location.href` 跳转之后，同一场浏览器里标题框和 CodeMirror 的 `send_keys` 都不进字。当前做法是 `cm.focus()` + `cm.execCommand('selectAll')`，再逐字 `driver.execute_cdp_cmd("Input.insertText", {"text": char})`。第一字替换选区，其余字追加。editor.md 有延迟同步，断言要等 CodeMirror 和 `#content` 都等于目标正文。隐藏输入框里的 `Ctrl+A` 也选不中正文。
- 列表用户名一开始可能是页面里的占位文字，要等到变成 `zhangsan` 再断言。
- `edit` 会打到线上。清理逻辑只删本用例创建的时间戳标题。

## 还可以继续的事

1. 磁盘目录仍叫 `Forum_system_testing`。真要改文件夹名，需要同步改工作区、`PYTHONPATH`、README 里的命令路径，以及可能的 Cursor 工作区绑定。
2. 逐字输入目前只覆盖写博客页发布。更新页 `blog_update.html` 还是脚本写入正文。
