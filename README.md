<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="Knowledge Base Builder 把搭建第二大脑变成一条稳定流程">
</p>

**English**: [README.en.md](./README.en.md) · **中文**: README.md

知识库搭建器（Knowledge Base Builder）是一个 Agent 通用的 Skill：引导你 3 分钟搭出一个结构化的「第二大脑」知识库。任何具备「读写文件 + 提问」能力的 Agent 都能执行。

你不用懂任何知识管理理论，说一句「帮我搭知识库」，它就会问你几个问题，然后用脚本确定地生成一套结构——不会漏目录、不会重复建，信息没想好也有默认值，不卡你。

## 你会得到什么

- `00-Inbox`：入口，新东西先丢这里，不分类
- `10-Areas`：已掌握的知识，按领域分
- `20-Projects`：项目，按 ing / done / wait 分
- `30-Output`：输出，按 ing / done / wait 分
- `40-Skills`：AI 协作工具
- `90-你的大脑说明`：个人档案，让 AI 认识你

外加三个核心文件：`README.md`（总览）、`个人档案.md`（你的画像）、`初始化提示词.md`（换新会话时发送，AI 秒接上）。

## 截图

**生成的知识库结构**（在 Obsidian 中打开的样子）：

![知识库结构](assets/readme/kb-structure.png)

**知识流转逻辑**（核心不是存储，是流转）：

![知识流转](assets/readme/kb-flow.png)

## 特性

- ✅ **通用**：核心流程只用「读写文件 + 提问」，不依赖任何特定 Agent 的专有功能
- ✅ **鲁棒**：信息不全有默认值，分步执行，出错可重试，不卡住
- ✅ **稳定**：骨架由脚本确定性生成，已存在结构时拒绝覆盖
- ✅ **结构化**：Inbox → Areas → Projects → Output 四层流转，知识可沉淀可复用

## 安装

告诉 Agent：

```text
帮我安装「https://github.com/ivercurry99/knowledge-base-builder」这个 Skill。
```

或使用命令：

```shell
npx skills add ivercurry99/knowledge-base-builder
```

## 使用

安装后，对你的 Agent 说：

```text
帮我搭知识库
```

然后跟着引导回答几个问题即可。

## 知识库结构

```text
00-Inbox/         入口：新东西先丢这里
10-Areas/         已掌握的知识，按领域分
20-Projects/      项目：ing / done / wait
30-Output/        输出：ing / done / wait
40-Skills/        AI 协作工具
90-大脑说明/      个人档案，AI 了解你
```

**核心流转**：新东西 → 00-Inbox → 确认走向 → 10-Areas / 20-Projects / 30-Output

## 数据与边界

- 所有文件只在**本地**生成，不联网、不上传任何数据。
- **无需配置、无需密钥**。
- 检测到目标目录已有知识库结构时**不会覆盖**，先询问「补充」还是「重建」。
- 覆盖、删除、重建都必须先经你确认。

## 兼容性

| 范围 | 状态 |
|------|------|
| 核心流程 | 只依赖「读写文件 + 提问」，具备这些能力的 Agent 均可执行 |
| 骨架脚本 | Python 3.10+，仅标准库，跨 macOS / Windows / Linux |
| 无 Python 环境 | 支持：按 `references/file-templates.md` 手工创建同样结构 |
| 网络 | 不需要 |

## 设计思路

知识库的核心不是「存储」，是「流转」：

- 看到的东西先丢进 Inbox，不分类
- 消化后升格到 Areas，变成可复用的知识
- 做项目放 Projects，对外输出放 Output
- 每层有明确的作用，不混在一起

## 示例

完整示例见 [`examples/数据分析师示例.md`](examples/数据分析师示例.md)——一个「数据分析师」用本 skill 搭建出来的知识库长什么样。

## 开发与验证

```shell
# 脚本回归测试
python -m unittest discover -s tests -v
```

## License

[MIT](./LICENSE)
