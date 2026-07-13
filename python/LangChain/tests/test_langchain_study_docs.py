import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = PROJECT_ROOT / "docs" / "LangChain_study"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class LangChainStudyDocsTests(unittest.TestCase):
    def assert_doc_has_standard_sections(self, file_name: str) -> None:
        path = DOCS_DIR / file_name
        self.assertTrue(path.exists(), f"missing file: {path}")

        text = read_text(path)
        required_sections = [
            "## 脚本作用",
            "## 运行前提",
            "## 完整代码",
            "## 分段讲解",
            "## 执行流程",
            "## 关键对象与机制",
            "## 容易踩坑点",
            "## 可扩展方向",
        ]
        for section in required_sections:
            self.assertIn(section, text, f"{file_name} missing section: {section}")

    def test_readme_exists_with_core_sections(self) -> None:
        readme = DOCS_DIR / "README.md"
        self.assertTrue(readme.exists(), f"missing file: {readme}")

        text = read_text(readme)
        required_sections = [
            "# LangChain_study 学习文档",
            "## 学习地图",
            "## 推荐学习顺序",
            "## 脚本索引",
            "## 核心概念总览",
        ]
        for section in required_sections:
            self.assertIn(section, text)

    def test_core_script_docs_exist_with_standard_sections(self) -> None:
        for file_name in [
            "chat_model_all_params.md",
            "langchain_tool_creation_examples.md",
            "openai_to_deepseek_configurable.md",
            "openai_to_deepseek_with_prefix.md",
        ]:
            self.assert_doc_has_standard_sections(file_name)

    def test_test_script_docs_exist_with_standard_sections(self) -> None:
        for file_name in [
            "test.md",
            "test2.md",
            "test3.md",
            "test4.md",
        ]:
            self.assert_doc_has_standard_sections(file_name)


if __name__ == "__main__":
    unittest.main()
