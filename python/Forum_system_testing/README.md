# UI 自动化测试框架

这是一个基于 `selenium + unittest + Page Object` 的可复用 UI 自动化测试框架，适用于论坛类 Web 系统，也可以快速迁移到其他页面型系统。

## 目录结构

```text
Forum_system_testing/
|-- config/          # 配置层
|-- common/          # 公共能力，驱动、基类、日志、报告
|-- pages/           # 页面对象层
|-- tests/           # 测试用例层
|-- .env.example     # 环境变量示例
|-- requirements.txt # 依赖清单
|-- run.py           # 统一运行入口
```

## 框架能力

- 支持通过 `.env` 或命令行参数切换环境
- 支持统一驱动初始化和浏览器生命周期管理
- 支持页面对象封装，降低定位器和业务逻辑耦合
- 支持失败自动截图
- 支持输出日志文件
- 支持生成 HTML 测试报告
- 支持按套件执行 `login`、`list`、`edit`、`details` 或 `all`

## 环境准备

1. 创建环境变量文件

```powershell
copy .env.example .env
```

2. 安装依赖

```powershell
& .\.venv38\Scripts\python.exe -m pip install -r .\requirements.txt
```

## 运行方式

### 执行全部测试

```powershell
$env:PYTHONPATH='E:\python\Forum_system_testing'
& .\.venv38\Scripts\python.exe .\run.py
```

### 只执行登录套件

```powershell
$env:PYTHONPATH='E:\python\Forum_system_testing'
& .\.venv38\Scripts\python.exe .\run.py --suite login
```

### 指定地址并启用无头模式

```powershell
$env:PYTHONPATH='E:\python\Forum_system_testing'
& .\.venv38\Scripts\python.exe .\run.py --suite all --base-url http://127.0.0.1:9580 --headless
```

## 输出产物

- 失败截图输出到 `images/`
- 运行日志输出到 `logs/`
- HTML 报告输出到 `reports/`

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
- 默认测试地址为 `http://127.0.0.1:9580`
- 执行前请确保被测系统已启动并可访问
