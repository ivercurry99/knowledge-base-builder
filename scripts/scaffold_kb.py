#!/usr/bin/env python3
"""knowledge-base-builder 的骨架生成脚本。

只使用 Python 3.10+ 标准库，跨 macOS / Windows / Linux。

用法：
  check <目录>                             检测目标目录是否已有知识库结构
  build <目录> --name <昵称> [更多参数]     生成骨架与核心文件

build 参数：
  --name <昵称>        默认「我」
  --occupation <职业>  默认「知识工作者」
  --areas <领域>       领域，可带子领域，见下
  --goal <目标>        默认「搭建第二大脑，让知识可沉淀、可复用」

--areas 格式（逗号分隔领域，冒号后跟该领域的子领域，分号分隔多个带子领域的领域）：
  "数据分析,AI工具"                                   → 两个领域，无子领域
  "数据分析:业务理解,分析思维,技术工具,项目实战;AI工具:提示词,Agent"  → 带子领域

约定：已存在同名目录或知识库结构时拒绝覆盖，返回退出码 2。
生成产物：根 README + 00-Inbox（含镜像领域的待沉淀）+ 10-Areas（含子领域）
+ 20-Projects + 30-Output + 40-Skills（含 hub README）
+ 90-{昵称}的大脑说明/ 下的 6 个核心文件。
"""
from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

if sys.version_info < (3, 10):
    sys.exit("需要 Python 3.10 或更高版本")

# 控制台编码不是 UTF-8 时（如 Windows CI 的 PowerShell），避免中文输出报错
for _stream in (sys.stdout, sys.stderr):
    if _stream and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            pass

ENCODING = "utf-8"
TODAY = datetime.date.today().isoformat()

PROJECT_DIRS = ["20-Projects/ing", "20-Projects/done", "20-Projects/wait"]
OUTPUT_DIRS = ["30-Output/ing", "30-Output/done", "30-Output/wait"]

STRUCTURE_MARKERS = ["README.md", "00-Inbox", "10-Areas", "20-Projects", "30-Output"]


def _parse_areas(raw: str) -> list[tuple[str, list[str]]]:
    """解析领域输入，返回 [(领域, [子领域...]), ...]。"""
    result: list[tuple[str, list[str]]] = []
    if not raw:
        return [("工作技能", []), ("个人成长", []), ("兴趣爱好", [])]
    for entry in raw.split(";"):
        entry = entry.strip()
        if not entry:
            continue
        if ":" in entry:
            domain, _, subs = entry.partition(":")
            domain = domain.strip()
            subs = [s.strip() for s in subs.split(",") if s.strip()]
        else:
            domain = entry.strip()
            subs = []
        if domain:
            result.append((domain, subs))
    return result or [("工作技能", []), ("个人成长", []), ("兴趣爱好", [])]


def _domains(areas: list[tuple[str, list[str]]]) -> list[str]:
    return [d for d, _ in areas]


def _area_dirs(areas: list[tuple[str, list[str]]]) -> list[str]:
    """10-Areas：领域纯名称，子领域带数字前缀。"""
    dirs = []
    for domain, subs in areas:
        dirs.append(f"10-Areas/{domain}")
        for i, sub in enumerate(subs, start=1):
            dirs.append(f"10-Areas/{domain}/{i}-{sub}")
    return dirs


def _inbox_dirs(areas: list[tuple[str, list[str]]]) -> list[str]:
    """00-Inbox：资源/灵感 + 待沉淀镜像领域（不含子领域）。"""
    dirs = ["00-Inbox/资源", "00-Inbox/灵感"]
    for domain, _ in areas:
        dirs.append(f"00-Inbox/待沉淀/{domain}")
    return dirs


def _all_dirs(areas: list[tuple[str, list[str]]], nickname: str) -> list[str]:
    return (
        _inbox_dirs(areas)
        + _area_dirs(areas)
        + PROJECT_DIRS
        + OUTPUT_DIRS
        + ["40-Skills", f"90-{nickname}的大脑说明"]
    )


def _fm(tags: list[str], type_: str, extra: dict | None = None) -> str:
    lines = ["---", "tags:"]
    for t in tags:
        lines.append(f"  - {t}")
    lines.append(f"created: {TODAY}")
    lines.append(f"type: {type_}")
    for k, v in (extra or {}).items():
        lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def _areas_text(areas: list[tuple[str, list[str]]]) -> str:
    return " · ".join(_domains(areas))


# ---------- 根 README ----------
def _root_readme(nickname: str, areas: list[tuple[str, list[str]]]) -> str:
    return (
        _fm(["README", "知识库"], "root")
        + f"# {nickname}的知识库\n\n"
        "> 既是思考的衍生，也是执行的燃料。\n\n"
        "---\n\n"
        "## 结构\n\n"
        "```text\n"
        "00-Inbox/         ← 入口：资源 / 灵感 / 待沉淀\n"
        f"10-Areas/         ← 已掌握：{_areas_text(areas)}\n"
        "20-Projects/      ← 项目：ing / done / wait\n"
        "30-Output/        ← 输出：ing / done / wait\n"
        "40-Skills/        ← AI 协作工具箱\n"
        f"90-{nickname}的大脑说明/ ← 对我的了解\n"
        "```\n\n"
        "## 流转\n\n"
        "```text\n"
        "新东西 → 00-Inbox → 你确认走向 → 10-Areas / 20-Projects / 30-Output\n"
        "```\n\n"
        "## AI 角色\n\n"
        "- 判断归属、提炼内容、生成初稿\n"
        "- 不替你决定走向\n"
        f"- 审慎更新 [[90-{nickname}的大脑说明/个人档案]]\n"
    )


# ---------- 大脑说明：说明书 ----------
def _brain_readme(nickname: str, areas: list[tuple[str, list[str]]]) -> str:
    rows = "\n".join(f"| `{d}` | 领域知识沉淀 | ✅ 已有 |" for d in _domains(areas))
    return (
        _fm(["索引", "核心档案"], "index")
        + f"# 🧠 {nickname}的大脑说明书\n\n"
        f"> 这里是 {nickname} 第二大脑的「使用说明书」。\n"
        f"> AI 助手协助 {nickname} 时，先读这里，再做事。\n\n"
        "---\n\n"
        "## 这个文件夹是什么\n\n"
        "这是整个知识库的最高优先级入口，回答三个问题：\n\n"
        f"1. {nickname} 是谁？ → [[个人档案]]\n"
        f"2. {nickname} 想要什么？ → [[个人档案#职业框架]] · [[个人档案#人生理想]]\n"
        "3. AI 怎么帮 TA？ → 见 [[agents|AI 操作约束]]\n\n"
        "---\n\n"
        "## AI 协作守则\n\n"
        "- 先理解，再行动：协作前先读 [[个人档案]]，不确定时主动问，不假设\n"
        "- 拆小任务、降低启动成本、及时反馈\n"
        "- 始终服务 [[个人档案#职业框架|三层职业框架]]，每次协作问一句「这件事服务于哪一层？」\n"
        "- 反焦虑：不鼓励收藏更多，鼓励消化、连接、输出\n\n"
        "---\n\n"
        "## 知识库地图\n\n"
        "| 文件夹 | 用途 | 状态 |\n"
        "|--------|------|------|\n"
        "| `00-Inbox` | 入口：资源 / 灵感 / 待沉淀 | 🟢 当前 |\n"
        "| `10-Areas` | 已掌握知识，按领域分 | ✅ 已有 |\n"
        f"{rows}\n"
        "| `20-Projects` | 项目：ing / done / wait | ✅ 已有 |\n"
        "| `30-Output` | 输出：ing / done / wait | ✅ 已有 |\n"
        "| `40-Skills` | AI 协作工具 | ✅ 已有 |\n"
        f"| `90-{nickname}的大脑说明` | 核心档案 + AI 协作说明 | 🟢 当前 |\n\n"
        "---\n\n"
        "## 更新日志\n\n"
        f"- {TODAY}：初版建立\n"
    )


# ---------- 大脑说明：个人档案 ----------
def _profile(nickname: str, occupation: str, areas: list[tuple[str, list[str]]], goal: str) -> str:
    return (
        _fm(["个人档案", "核心档案", f"{nickname}画像"], "profile", {"priority": "P0"})
        + f"> [!important] 这是 {nickname} 的核心身份档案 —— AI 的「了解 {nickname} 说明书」。\n"
        "> 任何 AI 助手协助之前，必须先读取本文件。\n\n"
        "---\n\n"
        f"# 👤 我对 {nickname} 的了解\n\n"
        "## 一、基本盘\n\n"
        "| 维度 | 信息 |\n"
        "|------|------|\n"
        f"| 昵称 | {nickname} |\n"
        f"| 职业 | {occupation} |\n"
        f"| 深耕领域 | {'、'.join(_domains(areas))} |\n"
        f"| 核心目标 | {goal} |\n\n"
        "---\n\n"
        "## 二、性格与协作适配\n\n"
        "> 待补充：TA 的性格特点，以及 AI 应该如何适配（例：喜欢条理 → 输出结构化）。\n\n"
        "---\n\n"
        "## 三、待进步点 & AI 怎么帮\n\n"
        "| # | 待进步点 | AI 配合策略 |\n"
        "|---|---------|-----------|\n"
        "| 1 | 待补充 | 待补充 |\n\n"
        "---\n\n"
        "## 四、职业框架（AI 决策的最高准则）\n\n"
        "```text\n"
        "第三层：爱好 + 擅长 → 人生故事输出\n"
        "        ↑\n"
        "第二层：主业衍生副业\n"
        "        ↑\n"
        "第一层：主业深耕\n"
        "```\n\n"
        "每次协作都问一句：「这件事服务于哪一层？」\n\n"
        "---\n\n"
        "## 五、人生理想\n\n"
        "> 待补充：TA 的「为什么」——AI 在长期协助中要始终记住的理想。\n\n"
        "---\n\n"
        "## 六、当前最大的痛点\n\n"
        "> 待补充：TA 现在最焦虑/最卡住的事，以及 AI 该怎么帮。\n\n"
        "---\n\n"
        "## 七、AI 协作风格指南\n\n"
        "| 场景 | AI 默认决策 |\n"
        "|------|-----------|\n"
        "| 想做但犹豫 | 支持 + 拆小 |\n"
        "| 想完美再发 | 先发再优化 |\n"
        "| 不清楚方向 | 回到职业框架 |\n\n"
        "---\n\n"
        "## 八、AI 永远不要忘记\n\n"
        "1. TA 是领导者，AI 是合伙人。\n"
        "2. 先对齐框架再动手。\n"
        "3. 快速出第一版然后迭代，不要等完美。\n\n"
        "---\n\n"
        "## 更新日志\n\n"
        f"- {TODAY}：初版建立\n"
    )


# ---------- 大脑说明：AI 操作约束 ----------
def _agents(nickname: str) -> str:
    return (
        _fm(["Harness", "约束"], "constraint")
        + "# AI 操作约束（Harness）\n\n"
        f"> 我在 {nickname} 的知识库里必须遵守的操作护栏。\n\n"
        "---\n\n"
        "## 1. 上下文常驻\n\n"
        "每次对话，默认加载：\n"
        f"- [[90-{nickname}的大脑说明/个人档案]]\n"
        "- [[README]]\n"
        "- 当前活跃项目的进度文件（如有）\n\n"
        "---\n\n"
        "## 2. 完成标准\n\n"
        "| 操作类型 | 完成标准 |\n"
        "|----------|----------|\n"
        "| 沉淀知识 | 来源已读 → 归属已确认 → 笔记已写入 → Inbox 已标记√ |\n"
        "| 创建文件 | 文件已写 → wiki-link 已验证 → 不产生死链 |\n"
        "| 移动文件 | 文件已移 → 全库链接已更新 → 旧路径残留为 0 |\n"
        "| 输出内容 | 初稿已生成 → 用户已确认 → 放入 Output 对应状态 |\n"
        "| 新增领域 | 用户已审批 → 目录已建 → README 已写 |\n"
        "| 更新大脑说明 | 观察 ≥2 次模式 + 用户同意 |\n\n"
        "---\n\n"
        "## 3. 文件操作约束\n\n"
        "- 写文件前必须先读\n"
        "- 移动目录前必须先确认目标结构\n"
        "- 批量操作前必须告知影响范围\n"
        f"- 永远不删除 `90-{nickname}的大脑说明/` 下的文件\n\n"
        "---\n\n"
        "## 4. 建议 vs 执行\n\n"
        "| 类型 | 规则 |\n"
        "|------|------|\n"
        "| 创建新领域/分类 | 必须经用户审批 |\n"
        "| 移动/重命名/删除文件 | 必须经用户确认 |\n"
        "| 提炼内容/生成初稿 | 可以先做，用户不满意再改 |\n\n"
        "---\n\n"
        "## 5. 结构规则\n\n"
        "| 规则 | 说明 |\n"
        "|------|------|\n"
        "| 单文件不放子文件夹 | 同一主题 ≥ 2 个文件才建子文件夹 |\n"
        "| 移动必更新链接 | 移动后全库更新 wiki-link，残留为 0 |\n"
        "| 新领域需审批 | 不批准不创建 |\n"
        "| 升格后标记来源 | 原文加 √ + 指向产出 |\n\n"
        "---\n\n"
        "## 6. 反馈循环\n\n"
        "用户说「不对」「太垃圾了」= 改进信号，不是否定。直接问「哪里要改」→ 快速出下一版。\n"
    )


# ---------- 大脑说明：初始化提示词 ----------
def _init_prompt(nickname: str, occupation: str, areas: list[tuple[str, list[str]]], goal: str) -> str:
    domain_list = "、".join(_domains(areas))
    return (
        _fm(["Skills", "初始化"], "skill", {"status": "active"})
        + "# 知识库初始化提示词\n\n"
        "> 换新电脑/新账号时，发这段给 AI，它就能接上现在的工作模式。\n\n"
        "---\n\n"
        "```\n"
        "## 我是谁\n\n"
        f"{nickname}，{occupation}。深耕{domain_list}。\n\n"
        "性格与工作风格：\n"
        "- 喜欢条理和整洁\n"
        "- 有创意但追求完美，毅力偶有不足——破解：快速出第一版然后迭代\n"
        "- 先搭框架再填内容\n"
        "- 反馈直接：「太垃圾了」= 改进信号\n\n"
        f"终极目标：{goal}。\n\n"
        "## 职业框架（三层标准）\n\n"
        "```text\n"
        "第三层：爱好+擅长 → 人生故事输出\n"
        "第二层：主业衍生副业\n"
        "第一层：主业深耕\n"
        "```\n\n"
        "**一鱼多吃原则**：一个动作能同时服务多层才是好任务。\n\n"
        "## 知识库结构\n\n"
        "```text\n"
        "00-Inbox/         ← 入口：资源 / 灵感 / 待沉淀\n"
        f"10-Areas/         ← 已掌握：{_areas_text(areas)}\n"
        "20-Projects/      ← 项目：ing / done / wait\n"
        "30-Output/        ← 输出：ing / done / wait\n"
        "40-Skills/        ← AI 协作工具箱\n"
        f"90-{nickname}的大脑说明/ ← 对我的了解\n"
        "```\n\n"
        "流转规则：新东西 → 00-Inbox → 确认走向 → 10-Areas / 20-Projects / 30-Output。走向必须经过确认。\n\n"
        "## 知识沉淀流程\n\n"
        "1. 读完整理解 → 2. 判断归属 → 3. 问确认 → 4. 写成结构化笔记 → 5. 放入对应 Area → 6. 原文加 √ + 指向产出\n\n"
        "## 沉淀标准\n\n"
        "- 读完能讲给别人听 → 合格\n"
        "- 信息密度不是目标，逻辑完整能掌握才是\n"
        "- 不遗漏知识点，不压缩过度\n\n"
        "### 两种沉淀模式（用户不说就主动问）\n\n"
        "| 用户说 | 怎么做 |\n"
        "|--------|--------|\n"
        "| 「小白式沉淀」 | 大白话、生活类比、场景引入、假设零基础 |\n"
        "| 「知识沉淀」/ 没说 | 保留原文信息密度，不精简过头，关键细节不能丢 |\n\n"
        "### 沉淀必须保留的信息\n\n"
        "- 原文中的资源来源必须保留\n"
        "- 原文中的具体数字、表格、步骤不能省略\n"
        "- 原文中的案例不能省略\n"
        "- 每篇开头用场景引入，中间用类比解释，结尾链到相关笔记\n\n"
        "## Areas 知识架构原则\n\n"
        "- 认知层用 frontmatter 标签分层，不建文件夹\n"
        "- 每个领域有自己的分类方式（子领域带数字前缀）\n"
        "- 领域知识不混合，跨领域链接只在自然关联时建立\n"
        "- 升格后必须更新 Area README 索引\n"
        "- 知识架构随沉淀逐步建立，用 Obsidian 图谱 + 双向链接\n\n"
        "## 待沉淀 → Areas 升格三标准\n\n"
        "1. 能用自己的话讲清楚\n"
        "2. 在工作中或生活中用过\n"
        "3. 能教给别人\n\n"
        "## 文件命名规则\n\n"
        "- 同一主题 ≥2 个文件才建子文件夹，单个放 Area 根目录\n"
        "- 有逻辑顺序标数字（1-、2-），无逻辑顺序用字母（A-、B-）\n"
        "- 文件夹名匹配待沉淀目录名\n\n"
        "## 日常约定\n\n"
        "- 待沉淀中已处理的文件，文件名末尾加 √\n"
        "- Areas 文件夹名必须匹配待沉淀目录名\n"
        "- Projects 和 Output 各有 ing/done/wait 三个子目录\n"
        "- 文件重命名/移动后：更新全库 wiki-link，验证残留为 0\n"
        "- 敏感信息（密码/密钥）不放知识库\n\n"
        "## 文件操作铁律\n\n"
        "- 写前必须先读。移动前先确认目标。批量前先告知范围\n"
        "- 移动后全库更新 wiki-link，验证残留为 0\n"
        f"- 永远不删 90-{nickname}的大脑说明/\n"
        "- 新领域必须先问审批再创建\n\n"
        "## 我的偏好\n\n"
        "- 输出风格：结构化（标题+列表+表格）、可视化、卡片化、白话不装\n"
        "- 不要长篇纯文字、不要含糊的「看你需求」、不要盲目捧\n"
        "- 不要过度拆文件夹\n"
        "- 知识库宁可简化不要复杂化\n\n"
        "## AI 反焦虑铁律\n\n"
        "| ❌ 不要 | ✅ 要 |\n"
        "|--------|------|\n"
        "| 推荐收藏更多 | 激活已有收藏 |\n"
        "| 一次给 100 个知识点 | 一次 1-3 个，真正吸收 |\n"
        "| 「先存着以后看」 | 「现在就消化成卡片」 |\n\n"
        "## 沟通风格\n\n"
        "- 务实、求真、不盲从，说错了指出来\n"
        "- 用户是领导者，AI 是合伙人 + 执行者\n"
        "- 「太垃圾了」= 改进信号，直接问「哪里要改」\n"
        "- 先对齐框架再动手\n\n"
        "## 门禁（Harness）\n\n"
        "| 操作 | 完成标准 |\n"
        "|------|----------|\n"
        "| 沉淀知识 | 来源已读 → 归属已确认 → 笔记已写入 → Inbox 已标记√ |\n"
        "| 移动文件 | 已移 → 全库链接已更新 → 残留为 0 |\n"
        "| 输出内容 | 初稿已生成 → 用户已确认 → 放入 Output 对应状态 |\n"
        "| 新增领域 | 用户已审批 → 目录已建 → README 已写 |\n\n"
        "## 关键文件（必读）\n\n"
        f"- 我的完整档案：90-{nickname}的大脑说明/个人档案.md\n"
        "- 知识库总览：README.md\n"
        f"- AI 操作约束与规则：90-{nickname}的大脑说明/agents.md\n\n"
        "现在读取上面几个关键文件，确认理解工作模式。然后告诉我你准备好了，我们继续。\n"
        "```\n"
    )


# ---------- 大脑说明：文件追踪 ----------
def _file_tracking() -> str:
    return (
        _fm(["Skills", "文件追踪"], "skill")
        + "# 文件追踪系统\n\n"
        "> 当你重命名或移动文件时，AI 负责更新所有相关链接。\n\n"
        "---\n\n"
        "## 追踪机制\n\n"
        "```text\n"
        "你说「我改了文件名」或「我移动了文件」\n"
        "        ↓\n"
        "重新扫描全库 → 对比基线 → 找出变化\n"
        "        ↓\n"
        "变化类型：\n"
        "├─ 新增文件 → 更新索引\n"
        "├─ 删除文件 → 检查悬空链接\n"
        "├─ 重命名   → 更新所有 旧名 → 新名\n"
        "└─ 移动     → 更新所有路径引用\n"
        "```\n\n"
        "## 自动修复范围\n\n"
        "| 变化 | 自动修复 |\n"
        "|------|---------|\n"
        "| 文件重命名 | 全库所有旧文件名的 wiki-link |\n"
        "| 文件移动 | 全库所有指向旧路径的链接 |\n"
        "| 删除文件 | 标记悬空链接 |\n\n"
        "## 使用方式\n\n"
        "- 「我把 XX 文件改名了」→ 更新所有链接\n"
        "- 「我移动了 XX 到 YY 目录」→ 同上\n"
        "- 「帮我检查有没有断链」→ 扫描全库 wiki-link\n"
    )


# ---------- 大脑说明：备份方案 ----------
def _backup() -> str:
    return (
        _fm(["Skills", "备份"], "skill")
        + "# 知识库备份\n\n"
        "> 知识全在本地磁盘，需要定期备份。\n\n"
        "---\n\n"
        "## 方案 A：GitHub 私有仓库（推荐）\n\n"
        "```bash\n"
        "cd <知识库目录>\n"
        "git init && git add -A && git commit -m \"init\"\n"
        "git remote add origin <你的私有仓库地址>\n"
        "git push -u origin main\n"
        "```\n\n"
        "## 方案 B：本地压缩备份（备用）\n\n"
        "```bash\n"
        "Compress-Archive -Path \"<知识库目录>\" -DestinationPath \"<备份目录>/知识库-$(Get-Date -Format yyyyMMdd).zip\"\n"
        "```\n\n"
        "## 备份频率建议\n\n"
        "| 频率 | 触发条件 |\n"
        "|------|---------|\n"
        "| 每次大改动后 | 移动目录、批量链接更新、结构变更 |\n"
        "| 每周 | 正常使用 |\n"
        "| 发布输出前 | 对外内容发布前 |\n\n"
        "## 当前状态\n\n"
        "- [ ] GitHub 私有仓库已建立\n"
        "- [ ] 首次备份已完成\n"
    )


# ---------- 40-Skills：hub ----------
def _skills_readme(nickname: str) -> str:
    return (
        _fm(["知识库优化", "Skills", "AI协作"], "skill-hub", {"status": "active"})
        + "# Skills — 执行工具箱\n\n"
        f"> 我在帮 {nickname} 执行任务时用到或已经装好的技能。\n\n"
        "---\n\n"
        "## 当前已有 Skills\n\n"
        "| Skill | 用途 | 状态 |\n"
        "|-------|------|------|\n"
        "| （待补充） | 按需安装 | — |\n\n"
        "---\n\n"
        "## 需要时再装的 Skills\n\n"
        "- 按实际需要安装，不提前囤积\n"
    )


def has_structure(root: Path) -> bool:
    return sum(1 for m in STRUCTURE_MARKERS if (root / m).exists()) >= 2


def cmd_check(root: Path) -> int:
    if has_structure(root):
        print(f"已存在知识库结构：{root}")
        return 0
    print(f"未检测到知识库结构：{root}")
    return 1


def _build_files(
    nickname: str,
    occupation: str,
    areas: list[tuple[str, list[str]]],
    goal: str,
) -> dict[str, str]:
    brain = f"90-{nickname}的大脑说明"
    return {
        "README.md": _root_readme(nickname, areas),
        "40-Skills/README.md": _skills_readme(nickname),
        f"{brain}/README.md": _brain_readme(nickname, areas),
        f"{brain}/个人档案.md": _profile(nickname, occupation, areas, goal),
        f"{brain}/agents.md": _agents(nickname),
        f"{brain}/初始化提示词.md": _init_prompt(nickname, occupation, areas, goal),
        f"{brain}/文件追踪.md": _file_tracking(),
        f"{brain}/备份方案.md": _backup(),
    }


def cmd_build(root: Path, args: argparse.Namespace) -> int:
    nickname = args.name or "我"
    occupation = args.occupation or "知识工作者"
    goal = args.goal or "搭建第二大脑，让知识可沉淀、可复用"
    areas = _parse_areas(args.areas)

    if has_structure(root):
        print(f"[拒绝] 目标目录已存在知识库结构：{root}")
        print("如确需重建，请先确认并移除旧结构，或换一个空目录。")
        return 2

    try:
        for rel in _all_dirs(areas, nickname):
            (root / rel).mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        print(f"[失败] 目录已存在，已停止，未覆盖任何已有文件：{exc}")
        return 2

    files = _build_files(nickname, occupation, areas, goal)
    for rel, content in files.items():
        (root / rel).write_text(content, encoding=ENCODING)

    print(f"已生成知识库骨架：{root}")
    print(f"目录 {len(_all_dirs(areas, nickname))} 个，文件 {len(files)} 个。")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="知识库骨架生成器")
    sub = parser.add_subparsers(dest="cmd", required=True)

    check = sub.add_parser("check", help="检测目标目录是否已有知识库结构")
    check.add_argument("root", type=Path)

    build = sub.add_parser("build", help="生成知识库骨架与核心文件")
    build.add_argument("root", type=Path)
    build.add_argument("--name", default="")
    build.add_argument("--occupation", default="")
    build.add_argument("--areas", default="")
    build.add_argument("--goal", default="")

    args = parser.parse_args(argv)
    if args.cmd == "check":
        return cmd_check(args.root)
    return cmd_build(args.root, args)


if __name__ == "__main__":
    raise SystemExit(main())
