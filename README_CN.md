[English](./README.md) | 简体中文

# Gemini Commit Guard - DevOps 全栈平台 (V4)

这是一个企业级的、全栈式 **Git 提交审计平台**，由 **Google Gemini 2.0 Flash** 驱动。
它不仅能在终端拦截 Bug，还配备了一个**可视化监控台 (Dashboard)**，让你能回溯每一次提交的历史、审计安全风险，并监控项目的代码质量趋势。

## 💡 愿景：从“工具”到“平台”

**痛点：**
1.  **Bug 隐形**：传统的 Linter 无法理解跨文件的逻辑错误。而且终端里的报错信息是“瞬时”的，窗口一关，教训就忘了。
2.  **黑盒操作**：当 Hook 拦截提交后，没有任何历史记录可以复盘“为什么被拦截”或者“我们最近犯了多少错”。

**解决方案：** 一个闭环系统。
1.  **主动防御 (Guard)**：利用 AI 的上下文理解能力，在 Commit 阶段拦截逻辑错误和安全风险。
2.  **全链路可观测性 (Observability)**：将每一次的代码变更 (Diff) 和 AI 诊断报告存入本地数据库，并通过可视化界面进行回溯。

## 📜 开发日志 (项目演进之路)

这个项目不仅仅是一个脚本，它经历了一次完整的工程化演进：

### 阶段一：Shell 概念验证 (V1 & V2)
* **目标**：验证 `git diff` 可以被 AI 分析并拦截提交。
* **教训**：Windows 的换行符问题 (`CRLF`) 让 Shell 脚本难以跨平台维护。
* **突破**：V2 引入了 **上下文感知**——不仅发送 Diff，还读取文件的完整内容，成功检测出了单纯看 Diff 无法发现的 Bug。

### 阶段二：Python 工程化重构 (V3)
* **目标**：稳定性与架构升级。
* **成果**：使用 Python 重写核心逻辑。引入 `GitClient` 封装底层操作，使用 Google 官方 SDK 替代 CLI，并引入虚拟环境隔离。

### 阶段三：“话痨 AI”事故与 JSON 模式 (V3.5)
* **Bug**：AI 因为觉得代码写得太好，返回了一篇赞美代码的“小作文”。但这篇作文里引用了代码中的 `[WARNING]` 字符串，导致我们的解析逻辑自相矛盾，拦截了正常的提交！
* **修复**：我们放弃了脆弱的字符串匹配。
* **实现**：启用了 Gemini 的 **Native JSON Mode** (`response_mime_type="application/json"`)，强制 AI 输出结构化数据，实现了 100% 的解析稳定性。

### 阶段四：全栈可观测性 (V4) 🚀
* **目标**：实现“有记忆”的审计。
* **技术栈**：引入 **SQLite** 做持久化，**Streamlit** 做可视化前端。
* **成果**：构建了一个 Dashboard，可以统计通过/失败率，并支持点击展开查看任意一次历史提交的 Diff 和 AI 诊断详情。

---

## 🚀 安装指南

### 1. 环境准备
* Python 3.8+
* Git
* Google Gemini API Key ([点击这里获取](https://aistudio.google.com/app/apikey))

### 2. 环境搭建 (只需一次)

在项目根目录下运行：

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活环境并安装依赖
# (Windows Git Bash 使用: source venv/Scripts/activate)
source venv/Scripts/activate

# 安装 SDK 和 Dashboard 工具
pip install google-generativeai streamlit pandas
pip freeze > requirements.txt

# 3. 配置环境变量
export GEMINI_API_KEY="YOUR_API_KEY_HERE"
````

### 3\. 安装 Git 钩子

我们需要安装一个 Shell "垫片" (Shim) 来连接 Git 和 Python 环境。运行以下命令直接覆盖旧钩子：

```bash
cp pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

-----

## 📊 使用说明与监控台

### 1\. 自动守卫 (终端模式)

像往常一样提交代码。

```bash
git commit -m "Refactor logic"
```

  * **如果安全**：提交通过，绿色提示。
  * **如果风险**：提交被拦截，红色警告。
  * **日志**：所有记录都会自动存入 `.gemini_audit.db`。

### 2\. 可视化监控台 (GUI 模式) 🆕

想查看审计历史或深度分析错误原因？运行：

```bash
streamlit run src/dashboard.py
```

浏览器将自动打开监控台，你可以：

  * 📈 **查看指标**：侧边栏实时显示代码提交的“通过率”与“拦截率”。
  * 📜 **审计历史**：完整的时间轴记录。每一次提交是成功还是被拦截，一目了然。
  * 🔍 **深度诊断**：点击任意一条记录即可展开。你可以对照查看当时的 **代码变更 (Diff)** 和 **AI 的详细 JSON 诊断报告**。

-----

## 🏗️ 系统架构

```text
gemini-guard/
├── src/
│   ├── main.py          # 逻辑控制器
│   ├── git_client.py    # 数据层: Git 操作
│   ├── ai_engine.py     # 服务层: Gemini API (JSON 模式)
│   ├── audit_logger.py  # 持久层: SQLite 管理
│   └── dashboard.py     # 展示层: Streamlit Web App
├── venv/                # 隔离环境
├── .gemini_audit.db     # 本地数据库 (自动生成)
└── pre-commit           # Shell 垫片
```

## 🧪 核心能力

  * **SQL 注入防御**: 主动识别危险的字符串拼接。
  * **上下文感知**: 读取完整文件以校验变量定义和作用域。
  * **强壮的 JSON 解析**: 免疫“Prompt 注入”或 AI 的废话干扰。
  * **全历史审计**: 数据本地持久化，随时回溯安全隐患。

-----

## 🔮 产品规划：迈向 V5 一体化

我们正在将 Gemini Guard 从一个“Python 脚本工具”转型为一款 **“独立运行的 DevOps 审计产品”**。

### 🔜 里程碑 1：中央集权 (V4.5)

  * **全局数据库**: 将数据存储迁移至用户主目录 `~/.gemini-guard/`，建立全局唯一的数据中心。
  * **多项目支持**: 数据库表结构升级，支持按项目隔离日志。在一个 Dashboard 中管理你的 10+ 个代码仓库。

### 🔜 里程碑 2：零依赖交付 (V5)

  * **二进制分发**: 使用 **PyInstaller** 将 Python 环境、SDK 和 UI 框架打包成独立的 `.exe` 或二进制文件。
  * **面向全栈**: 让前端、Java、Go 等非 Python 开发者也能“零配置”使用，无需安装 Python 或 Pip。

### 🔜 里程碑 3：极致体验

  * **`gg init`**: 引入全新的 CLI 初始化命令，一键识别当前仓库，自动挂载 Hook 并注册项目。
  * **统一监控台**: 升级可视化界面，支持侧边栏切换项目，在一个窗口内监控所有项目的代码质量趋势。

