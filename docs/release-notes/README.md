# 这个目录放「手写 Release Notes」

命名规则：`v<版本>.md`，例如 `v2.1.0.md`。

- **存在**同名文件 → Release 正文用它（`gh release create --notes-file`）。
- **不存在** → 用 GitHub 自动生成的 notes（`--generate-notes`，会把合并的 PR 和提交列表整理出来）。

正文里可以写版本亮点、破坏性变更、升级注意。附件不用写，工作流自动带上两个 exe、zip 和 SHA256SUMS.txt。
