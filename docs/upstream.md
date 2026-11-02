# 上游核实记录（pojia-next）

本文档只记录**可复核的事实**：URL、抓取方式、原文片段。核实日期 **2026-11-02**。

---

## 1. 上游标识

| 项 | 值 |
|---|---|
| 仓库 | <https://github.com/z91772524-ai/pojia-next> |
| 名称 | 破甲一键通（pojia-next） |
| 默认分支 | `main`（从仓库页 HTML 的 `defaultBranch":"main"` 字段读出） |
| 作者/维护者 | z91772524-ai |
| 许可证 | **MIT** |
| 形态 | 图形程序 + 单文件 exe（Release 附件）；README 声明「源码不再随仓库分发」 |

## 2. 许可证原文

抓取 URL（两个都试了，字节一致，以 `main` 为准）：

- <https://raw.githubusercontent.com/z91772524-ai/pojia-next/main/LICENSE> → HTTP 200，1069 字节
- <https://raw.githubusercontent.com/z91772524-ai/pojia-next/master/LICENSE> → HTTP 200，1069 字节

原文开头片段（逐字）：

```text
MIT License

Copyright (c) 2026 z91772524-ai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

原文结尾片段（逐字）：

```text
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

结论：**标准 MIT，无附加条款，无 copyleft**。因此本项目 LICENSE 只能、也只采用 MIT，并保留 `Copyright (c) 2026 z91772524-ai`。

## 3. 仓库页证据

抓取 <https://github.com/z91772524-ai/pojia-next>（HTTP 200）。页面 README 渲染内容中的相关片段：

许可证徽章（逐字）：

```text
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
```

署名段（逐字，节选，省略其中各仓库链接）：

```text
> ### 🙏 本项目的破甲来自谁（署名）
> **破甲思路与部分实现来源（排名不分先后，各自实现，MIT 署名与许可要求均已保留）：**
> [@YuJunZhiXue / dsh-purge]（DSH 破甲的原始项目）、
> [@kingcharleslzy-ai / dsh-purge]（社区版）、
> …
> 本项目由 **@z91772524-ai** 维护（代码、文档、发布）；逐条对照见 [思路与致谢]。
```

支持范围（逐字）：

```text
支持 **DSH / WorkBuddy / ZCode / Codex / Cursor / Claude Code / Gemini CLI / Qwen Code / iFlow / Trae / CodeBuddy / OpenCode / Windsurf / Cline / Copilot CLI** 十五个客户端
```

发行形态（逐字）：

```text
**图形界面（原生窗口）+ 单文件 exe**：不装 Python、不敲命令、不进浏览器；
仓库只发成品 exe（Release 附件），源码不再随仓库分发。
```

风险自述（逐字）：

```text
⚠️ **风险提示**：本工具修改第三方客户端的本地提示词文件，处于客户端使用条款的灰色地带 —— **账号风险自负**。介意者请勿使用，或用完即「还原」。
```

对二次发布的态度（逐字，节选）：

```text
第三方发布的「**WKBD rev1.0 / rev2.0**」（化名 `popopo`）是基于本项目**换皮二次发布**，
且把 MIT 强制保留的版权声明删空成 `Copyright (c) 2026`。
```

## 4. 抓取方式与局限

- 工具：本会话的 `web_fetch`（HTTP 直取 + 浏览器回退）。
- `LICENSE.md` 不存在（HTTP 404），许可证就在 `LICENSE`。
- GitHub REST API `api.github.com/repos/z91772524-ai/pojia-next` 本次**未能取到 JSON**（返回速率限制页面），因此 star 数、创建时间、仓库描述等字段**未核实**，本文档不作断言；许可证结论来自 LICENSE 原文与仓库页面徽章两条独立证据。
- 上游 README 中提到的站外官网、交流群等链接，本仓库**不转载、不引用**（本仓库不含广告位与群号）。
- 上游源码未随仓库分发，因此「本仓库重写实现与上游源码的逐行对应关系」**未核实**；本仓库只声明「取用了 WorkBuddy 补丁引擎的行为契约」，依据是上游 README 声称覆盖 WorkBuddy，以及本项目重写时所依据的同一套靶点行为。

## 5. 由此产生的许可动作

1. `LICENSE` 采用 MIT，保留上游版权行 + 本项目版权行。
2. `NOTICE` 写明派生关系、取用范围、未取用部分与非官方声明。
3. `README.md` / `README.zh.md` 顶部给出上游链接与 MIT 说明。
4. 不删除、不改写上游版权声明（MIT 的强制条件）。
