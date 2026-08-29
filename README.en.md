<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="Knowledge Base Builder: scaffold your second brain in 3 minutes with a four-layer flow from 00-Inbox to 10-Areas / 20-Projects / 30-Output">
</p>

<p align="center">
  <a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-8a5cf5"></a>
  <a href="https://github.com/ivercurry99/knowledge-base-builder/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/ivercurry99/knowledge-base-builder/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-50a0fa?logo=python&logoColor=white">
  <img alt="Platform" src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-4a4a52">
  <img alt="Network" src="https://img.shields.io/badge/network-not%20required-2ea043">
  <img alt="Last commit" src="https://img.shields.io/github/last-commit/ivercurry99/knowledge-base-builder?color=50a0fa">
  <img alt="Stars" src="https://img.shields.io/github/stars/ivercurry99/knowledge-base-builder?style=social">
</p>

<p align="center"><b>English</b>: README.en.md · <b>中文</b>: <a href="./README.md">README.md</a></p>

---

Knowledge Base Builder is an **agent-agnostic Skill** that guides you to scaffold a structured "second brain" knowledge base in about 3 minutes. Any agent with "read/write files + ask questions" capabilities can run it.

You don't need any knowledge-management theory. Say "help me build a knowledge base", answer a few questions, and it generates a structure deterministically with a script — **no missing folders, no duplicates, sensible defaults when you don't have an answer yet**.

## Table of contents

- [What the result looks like](#what-the-result-looks-like)
- [What problem it solves](#what-problem-it-solves)
- [Features](#features)
- [Quick start](#quick-start)
- [A full example](#a-full-example)
- [Data & boundaries](#data--boundaries)
- [Compatibility](#compatibility)
- [Design](#design)
- [Development](#development)
- [Acknowledgments & trademarks](#acknowledgments--trademarks)
- [License](#license)

## What the result looks like

**Knowledge flow** (the core is flow, not storage):

![Knowledge flow](assets/readme/kb-flow.png)

**Generated knowledge base structure** (opened in Obsidian):

![Knowledge base structure](assets/readme/kb-structure.png)

```text
00-Inbox/         entry: dump new things here
10-Areas/         digested knowledge, by domain
20-Projects/      projects: ing / done / wait
30-Output/        output: ing / done / wait
40-Skills/        AI collaboration tools
90-your-brain/    personal profile so the agent knows you
```

**Core flow**: new things → 00-Inbox → confirm direction → 10-Areas / 20-Projects / 30-Output

The brain folder (`90-your-brain/`) comes with 6 files at once: `README` (manual), `个人档案` (your profile), `agents` (operating constraints), `初始化提示词` (a full reset prompt covering the digestion workflow, promotion criteria, and gates), `文件追踪` (link auto-fix on file moves), and `备份方案` (backup plan). The agent reads this first.

## What problem it solves

| Without this skill | With this skill |
|--------------------|-----------------|
| Want a knowledge base, don't know where to start | One sentence, a few questions, done |
| Hand-creating folders — easy to miss / duplicate / agonize over names | Scripted, deterministic, idempotent, refuses to overwrite |
| Agent doesn't know how to help / you don't know what to ask | Ships a `90-your-brain` entry so the AI knows who you are |
| Stuck when info is incomplete | Every field has a default, never blocks |

## Features

- ✅ **Universal**: the core flow only needs "read/write files + ask questions", no host-specific features
- ✅ **Robust**: defaults for incomplete info, step-by-step execution, retryable on error
- ✅ **Stable**: the skeleton is generated deterministically by a script and refuses to overwrite existing structures
- ✅ **Structured**: Inbox → Areas → Projects → Output four-layer flow

## Quick start

**Option 1: ask your agent to install**

Tell your agent:

```text
Install this Skill: https://github.com/ivercurry99/knowledge-base-builder
```

**Option 2: use the command**

```shell
npx skills add ivercurry99/knowledge-base-builder
```

**After install**, say:

```text
help me build a knowledge base
```

Then follow the guided questions. See [`SKILL.md`](./SKILL.md) for parameters and [`examples/数据分析师示例.md`](examples/数据分析师示例.md) for a full example.

## A full example

What a "data analyst" knowledge base built with this skill looks like — see [`examples/数据分析师示例.md`](examples/数据分析师示例.md).

Excerpt of the tree:

```text
xiaochen-kb/
├── 00-Inbox/resources/  00-Inbox/ideas/  00-Inbox/to-digest/{domain}/
├── 10-Areas/data-analysis/{1-business, 2-thinking, ...}
├── 20-Projects/{ing, done, wait}
├── 30-Output/{ing, done, wait}
├── 40-Skills/README.md
└── 90-xiaochen-brain/{README, profile, agents, init-prompt, file-tracking, backup}
```

## Data & boundaries

- All files are generated **locally**; nothing is uploaded or sent over the network.
- **No configuration, no credentials** required.
- If the target directory already has a knowledge base structure, it will **not overwrite** it — it asks whether to extend or rebuild first.
- Overwriting, deleting, or rebuilding requires your confirmation.

## Compatibility

| Scope | Status |
|-------|--------|
| Core flow | Only needs "read/write files + ask questions"; any capable agent can run it |
| Skeleton script | Python 3.10+, standard library only, cross-platform macOS / Windows / Linux |
| No Python available | Supported: create the same structure manually per `references/file-templates.md` |
| Network | Not required |

## Design

The core of a knowledge base is "flow", not "storage":

- Drop things into Inbox first, unclassified
- Promote digested knowledge into Areas for reuse
- Projects go into Projects, published work goes into Output
- Each layer has a clear role and they don't mix

Full design rationale: [`references/design-principles.md`](references/design-principles.md).

## Development

```shell
# regression tests for the scaffold script
python -m unittest discover -s tests -v
```

CI runs the same suite on macOS / Windows / Linux in parallel — cross-platform parity is a hard requirement.

## Acknowledgments & trademarks

- The layering is inspired by Tiago Forte's **PARA method** (Projects / Areas / Resources / Archives) and the "**second brain**" idea. **This project adapts the layers and flow rules independently and is not affiliated with, endorsed by, or partnered with Tiago Forte or Forte Labs.** "Second Brain" and "PARA" are trademarks of their respective owners; this repository refers to them conceptually only and claims no rights.
- The software shown in screenshots is **Obsidian** (`obsidian.md`). "Obsidian" and its logo are trademarks of Obsidian MD Inc.; this repository refers to it factually only, to show how the knowledge base opens, and claims no rights.
- Thanks to everyone who has publicly shared their practices on "digital gardens" and "second brain" — this project is an engineered distillation of those conversations.

## License

[MIT](./LICENSE) · Copyright © 2026 [ivercurry99](https://github.com/ivercurry99)
