"""scaffold_kb.py 的回归测试。"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import scaffold_kb  # noqa: E402


class TestScaffoldKb(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "知识库"

    def tearDown(self):
        self._tmp.cleanup()

    def _build(self, **kw):
        argv = ["build", str(self.root), "--name", kw.get("name", "小陈")]
        for key in ("occupation", "areas", "goal"):
            if key in kw:
                argv += [f"--{key}", kw[key]]
        return scaffold_kb.main(argv)

    def test_build_creates_structure(self):
        rc = self._build(
            occupation="数据分析师",
            areas="数据分析:业务理解,分析思维,技术工具,项目实战;AI工具:提示词,Agent;个人成长",
            goal="提升主业",
        )
        self.assertEqual(rc, 0)
        for rel in [
            "README.md",
            "00-Inbox/资源", "00-Inbox/灵感",
            "00-Inbox/待沉淀/数据分析", "00-Inbox/待沉淀/AI工具", "00-Inbox/待沉淀/个人成长",
            "10-Areas/数据分析", "10-Areas/AI工具", "10-Areas/个人成长",
            "10-Areas/数据分析/1-业务理解", "10-Areas/数据分析/4-项目实战",
            "10-Areas/AI工具/2-Agent",
            "20-Projects/ing", "20-Projects/done", "20-Projects/wait",
            "30-Output/ing", "30-Output/done", "30-Output/wait",
            "40-Skills/README.md",
        ]:
            self.assertTrue((self.root / rel).exists(), f"缺少 {rel}")

    def test_brain_folder_has_six_files(self):
        self._build(occupation="数据分析师", areas="数据分析,AI工具,个人成长")
        brain = self.root / "90-小陈的大脑说明"
        for name in ["README.md", "个人档案.md", "agents.md", "初始化提示词.md", "文件追踪.md", "备份方案.md"]:
            self.assertTrue((brain / name).exists(), f"大脑说明缺少 {name}")

    def test_files_have_frontmatter(self):
        self._build(occupation="数据分析师", areas="数据分析,AI工具,个人成长")
        root_readme = (self.root / "README.md").read_text(encoding="utf-8")
        profile = (self.root / "90-小陈的大脑说明" / "个人档案.md").read_text(encoding="utf-8")
        self.assertTrue(root_readme.startswith("---\ntags:"))
        self.assertIn("type: root", root_readme)
        self.assertIn("type: profile", profile)
        self.assertIn("priority: P0", profile)

    def test_init_prompt_covers_workflow(self):
        self._build(occupation="数据分析师", areas="数据分析,AI工具,个人成长")
        init = (self.root / "90-小陈的大脑说明" / "初始化提示词.md").read_text(encoding="utf-8")
        for keyword in ["沉淀流程", "升格三标准", "门禁", "文件命名规则", "反焦虑", "职业框架"]:
            self.assertIn(keyword, init, f"初始化提示词缺少 {keyword}")

    def test_build_refuses_overwrite(self):
        first = self._build()
        self.assertEqual(first, 0)
        second = self._build(name="小李")
        self.assertEqual(second, 2)

    def test_check(self):
        self.assertEqual(scaffold_kb.main(["check", str(self.root)]), 1)
        self._build()
        self.assertEqual(scaffold_kb.main(["check", str(self.root)]), 0)

    def test_default_areas(self):
        rc = self._build()
        self.assertEqual(rc, 0)
        for d in ["工作技能", "个人成长", "兴趣爱好"]:
            self.assertTrue((self.root / "10-Areas" / d).exists(), f"缺少默认领域 {d}")
            self.assertTrue((self.root / "00-Inbox" / "待沉淀" / d).exists(), f"待沉淀缺少 {d}")


if __name__ == "__main__":
    unittest.main()
