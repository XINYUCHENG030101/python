from selenium.webdriver.support.ui import WebDriverWait

from config import settings


def normalize_text(value):
    return (value or "").replace("\r\n", "\n").strip()


def editor_content(driver):
    return driver.execute_script(
        "var el = document.getElementById('content');"
        "return el ? el.value : '';"
    )


def wait_editor_ready(driver):
    WebDriverWait(driver, settings.EXPLICIT_WAIT).until(
        lambda current: current.execute_script(
            "return !!document.querySelector('#editor .CodeMirror')"
            " && !!document.getElementById('content');"
        )
    )


def wait_markdown_contains(driver, snippet):
    wait_editor_ready(driver)
    WebDriverWait(driver, settings.EXPLICIT_WAIT).until(
        lambda current: snippet in (editor_content(current) or "")
    )
    return editor_content(driver)


def set_markdown(driver, content):
    wait_editor_ready(driver)
    script = """
        var content = arguments[0];
        var cmEl = document.querySelector('#editor .CodeMirror');
        if (cmEl && cmEl.CodeMirror) {
            cmEl.CodeMirror.setValue(content);
            if (cmEl.CodeMirror.save) {
                cmEl.CodeMirror.save();
            }
        }
        var el = document.getElementById('content');
        if (el) {
            el.value = content;
        }
        return el ? el.value : '';
    """

    def _applied(current):
        current.execute_script(script, content)
        return normalize_text(editor_content(current)) == normalize_text(content)

    WebDriverWait(driver, settings.EXPLICIT_WAIT).until(_applied)
    return editor_content(driver)


def codemirror_value(driver):
    return driver.execute_script(
        "var cmEl = document.querySelector('#editor .CodeMirror');"
        "return cmEl && cmEl.CodeMirror ? cmEl.CodeMirror.getValue() : '';"
    )


def _wait_editor_text(driver, expected):
    expected = normalize_text(expected)

    def _applied(current):
        return (
            normalize_text(codemirror_value(current)) == expected
            and normalize_text(editor_content(current)) == expected
        )

    WebDriverWait(driver, settings.EXPLICIT_WAIT).until(_applied)
    return editor_content(driver)


def _insert_text(driver, text):
    driver.execute_cdp_cmd("Input.insertText", {"text": text})


def type_markdown(driver, content):
    # 页面自己跳转之后，这场浏览器里的 send_keys 不再进输入框。
    # 先选中占位正文，再逐字走 Chrome 的 insertText，第一字替换选区。
    wait_editor_ready(driver)
    if not content:
        raise ValueError("逐字输入的正文不能为空")
    driver.execute_script(
        """
        var cm = document.querySelector('#editor .CodeMirror').CodeMirror;
        cm.focus();
        cm.execCommand('selectAll');
        """
    )
    _insert_text(driver, content[0])
    for char in content[1:]:
        _insert_text(driver, char)
    return _wait_editor_text(driver, content)
