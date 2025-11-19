[English](./README.md) | 简体中文

# Gemini Commit Guard - Python 重构版 (V3)

这是一个企业级的 Git pre-commit 钩子，由 **Google Gemini 2.0 Flash** 驱动。它就像一位住在你终端里的 AI 架构师，在你执行 `git commit` 时，对代码进行深度语义分析和静态检查，在 Bug 污染代码库之前将其拦截。

> **项目演进史：**
> * **V1/V2 (旧版)**: Shell 脚本 + Node.js CLI (已归档为 `v1.0-shell-poc`)
> * **V3 (当前)**: 纯 Python 工程 + Google 官方 SDK + 虚拟环境隔离

## 💡 灵感来源 (Why?)

**传统的开发流程：** `git add .` -> `git commit` -> `git push`。
**结果：** 编译成功，但 push 之后污染了代码库，因为有隐形的语义 Bug。
**后续：** 回退代码 (revert)，本地疯狂找 Bug，好无趣，好无聊。

**解决方案：** 这个工具可以在 `commit` 指令被触发时，自动调用 Gemini 进行语义分析。它能捕捉到那些编译器发现不了的“隐形” Bug（比如跨文件的变量拼写错误）。好好玩，老板再也不担心潜在的 Bug 污染代码库了！

## 🚀 为什么要重构为 Python?

虽然 V1 证明了想法可行，但 V3 带来了真正的工程成熟度：
* **架构设计**: 采用了模块化设计 (`GitClient`, `AIEngine`, `Main`)，逻辑清晰。
* **健壮性**: Python 的 `subprocess` 能比 Shell 脚本更优雅地处理 Git 输出、二进制文件和编码问题。
* **极速体验**: 使用了 Google 官方 Python SDK 调用最新的 `gemini-2.0-flash` 模型，响应极快。
* **环境隔离**: 运行在独立的虚拟环境 (`venv`) 中，不污染你的全局 Python 环境。

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
# (Mac/Linux 使用: source venv/bin/activate)
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

*(注：这个 `pre-commit` 脚本会自动激活 `venv` 并运行 Python 核心逻辑，你无需手动操作。)*

-----

## 🏗️ 系统架构

项目遵循清晰的模块化结构：

```text
gemini-guard/
├── src/
│   ├── main.py          # 程序入口 & 逻辑控制
│   ├── git_client.py    # Git 操作封装 (Diff 获取 & 上下文读取)
│   └── ai_engine.py     # AI 引擎 (封装 Google Generative AI SDK)
├── venv/                # 隔离的 Python 虚拟环境
├── requirements.txt     # 依赖锁定文件
└── pre-commit           # Shell Shim (Git 和 Python 之间的桥梁)
```

## 💻 使用方法

像往常一样提交代码即可！

```bash
git add .
git commit -m "My awesome feature"
```

  * **如果代码安全**: 显示 `[PASS]` -\> 提交成功。
  * **如果发现 Bug**: 显示 `[WARNING]` -\> 提交被拦截。你会直接在终端看到 AI 的详细分析报告。

-----

## 🧪 已验证的能力

  * **SQL 注入检测**: 能识别出危险的字符串拼接 SQL 查询。
  * **上下文感知 (Context Awareness)**: 能结合完整文件内容发现逻辑错误（例如：`diff` 中使用了 `MAX_RETRY`，但文件头部定义的是 `MAX_RETRIES`）。
  * **逻辑一致性**: 确保新增代码符合现有的类结构和设计模式。
