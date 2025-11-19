[English](./README.md) | 简体中文

# Gemini Commit Guard - Python 重构版 (V3.5)

这是一个企业级的 Git pre-commit 钩子，由 **Google Gemini 2.0 Flash** 驱动。它就像一位住在你终端里的 AI 架构师，在你执行 `git commit` 时，对代码进行深度语义分析和静态检查，在 Bug 污染代码库之前将其拦截。

## 💡 为什么开发这个工具？

**问题：** 传统的 CI/CD 流程是“反应式”的。Bug 往往在提交甚至合并后才被发现，导致不仅要回退代码，还要花大量时间在本地复现和调试。
**方案：** 主动式 AI 守卫。通过 Hook 拦截提交，我们利用 LLM 理解代码的“完整上下文”，捕捉那些 Linter 发现不了的逻辑错误（例如跨作用域的变量拼写错误）。

## 📜 开发日志 (项目演进之路)

这个项目不仅仅是一个脚本，它经历了一次完整的工程化演进：

### 第一阶段：Shell 概念验证 (V1 & V2)
* **目标**：验证 `git diff` 可以被 AI 分析并拦截提交。
* **挑战**：Windows 下的 `CRLF` 换行符和 `BOM` 编码问题导致脚本在不同机器上表现不一致。
* **突破**：V2 引入了 **RAG (检索增强生成)** 的雏形——不仅发送 Diff，还读取文件的完整上下文。这成功检测出了单纯看 Diff 无法发现的 Bug（如 `MAX_RETRY` 拼写错误）。

### 第二阶段：Python 工程化重构 (V3)
* **目标**：解决跨平台兼容性，引入模块化架构。
* **方案**：使用 Python 重写核心逻辑。
    * `git_client.py`: 封装 `subprocess` 处理 Git 操作。
    * `ai_engine.py`: 封装 Google 官方 SDK。
    * 引入 `venv` 虚拟环境实现依赖隔离。

### 第三阶段：“话痨 AI”事故与 JSON 模式 (V3.5)
* **Bug**：在重构后，AI 因为觉得代码写得太好，返回了一篇赞美代码的“小作文”。但这篇作文里引用了代码中的 `[WARNING]` 字符串，导致我们的解析逻辑误判，拦截了正常的提交！
* **修复**：我们放弃了脆弱的字符串匹配，转向了 **结构化工程**。
* **实现**：启用了 Gemini API 的 **Native JSON Mode** (`response_mime_type="application/json"`)，强制 AI 仅返回符合 Schema 的 JSON 数据，从而实现了 100% 的解析稳定性。

---

## 🚀 安装指南

### 1. 准备工作
* Python 3.8+
* Git
* Google Gemini API Key ([点击这里获取](https://aistudio.google.com/app/apikey))

### 2. 环境搭建 (只需一次)

在你的项目根目录下运行：

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活环境并安装依赖
# (Windows Git Bash 使用: source venv/Scripts/activate)
source venv/Scripts/activate
pip install google-generativeai
pip freeze > requirements.txt

# 3. 配置 API Key (建议添加到 ~/.bash_profile 或环境变量中)
export GEMINI_API_KEY="YOUR_API_KEY_HERE"
````

### 3\. 安装钩子 (Hook)

我们需要安装一个 Shell "垫片" (Shim) 来连接 Git 和 Python 环境。运行以下命令直接覆盖旧钩子：

```bash
# 复制垫片脚本
cp pre-commit .git/hooks/pre-commit

# 赋予执行权限
chmod +x .git/hooks/pre-commit
```

-----

## 🏗️ 系统架构

```text
gemini-guard/
├── src/
│   ├── main.py          # 逻辑控制 & JSON 解析器
│   ├── git_client.py    # Git 操作 (Diff & Context)
│   └── ai_engine.py     # AI 引擎 (原生 JSON 模式)
├── venv/                # 隔离环境
├── pre-commit           # Shell 垫片
└── requirements.txt     # 依赖列表
```

## 🧪 核心能力

  * **SQL 注入检测**: 识别危险的 SQL 拼接。
  * **上下文感知**: 读取完整文件以校验变量定义。
  * **强壮的 JSON 解析**: 免疫“Prompt 注入”或 AI 的废话干扰。
