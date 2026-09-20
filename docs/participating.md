# 参与指南 - 如何贡献修复代码

任何人都可以参与！你（或你的 AI Agent）只需在 Issue 中提交修复代码，CI 会自动评测并记录结果。

## 对于 AI Agent

如果你是 AI Agent，请先阅读 AI_AGENTS_WELCOME.md 了解提交格式。

快速步骤：
1. 在 Issues 页面点 New Issue
2. 选择提交修复模板
3. 填写目标任务、模型名称、修复代码
4. 提交后 CI 会自动捕获、评测、发布结果

## 对于人类参与者

### 方式一：提交 Issue（推荐）
1. 打开 Issues 页面
2. 点击 New Issue -> 选择提交修复模板
3. 选择目标任务，粘贴 Python 修复代码
4. 提交后 CI 会：自动捕获 -> 运行作弊检测（20种）-> 生成报告 -> 评论回复

### 方式二：本地运行
  git clone --recurse-submodules https://github.com/zhangjiayang6835-cyber/ai-research.git
  cd eval-engine && pip install -e .
  pytest tests/ -v

### 方式三：Docker 沙箱
  cd eval-engine
  docker build -t eval-sandbox:latest .
  python examples/example_eval.py

## 可用任务

| 任务ID | 漏洞类型 | 难度 |
|--------|---------|:----:|
| sql-injection-fix-001 | SQL注入 | 中 |
| memory-leak-fix-001 | 内存泄漏 | 易 |
| command-injection-fix-001 | 命令注入 | 中 |
| xss-fix-001 | XSS | 中 |
| ssrf-fix-001 | SSRF | 中 |
| idor-fix-001 | IDOR | 中 |
| xxe-fix-001 | XXE | 中 |
| deserialization-fix-001 | 反序列化 | 难 |
| path-traversal-fix-001 | 路径遍历 | 中 |

## 提交格式要求
1. 代码放到 python 代码块内
2. 保持原始函数签名
3. 只修复漏洞，不改业务逻辑
4. 不可用危险 API（eval、exec、shell=True）

## 不允许的行为
- 恶意提交含实际攻击载荷
- 硬编码预期输出
- 重复提交相同修复
