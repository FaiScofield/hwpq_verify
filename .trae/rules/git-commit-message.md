---
alwaysApply: true
scene: git_message
---

1. 提交信息应该只根据暂存的更改内容生成，不应该包含未暂存的文件。
2. 规范提交类型，只允许使用 "fix", "feat", "refactor", "style", "test", "docs", "perf", "chore" 等等。
3. 影响范围跟在提交类型后面，用中括号[]包含， 例如："fix[csc]"。
4. 首行应该是总结性语句，后续隔行开始描述更具体的更改内容，每个内容一句话总结，用 "- " 起始