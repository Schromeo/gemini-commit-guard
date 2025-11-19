[English](./README.md) | 简体中文
# Gemini Commit Guard - Shell POC (V1 & V2)

这是一个基于 Google Gemini CLI 的智能 Git pre-commit 钩子。它不仅仅是检查 Diff，还能读取文件上下文，像一位资深架构师一样在 `git commit` 时审查你的代码，防止 Bug 进入代码库。

## 灵感来源 (The "Why")

传统的开发流程：`git add .` -> `git commit` -> `git push`。
结果：编译成功，但 push 之后污染了代码库，因为有隐形的语义 Bug。
接下来：回退代码 (revert)，本地疯狂找 Bug，好无趣，好无聊。

而这个工具可以在 `commit` 指令被触发时，自动调用 Gemini 进行语义分析，在 Bug 进入代码库**之前**就将其拦截。好好玩，老板再也不担心潜在的 Bug 污染代码库了！

## 🏆 成果展示

### V1 成果：拦截危险代码 (Diff Analysis)
我们成功跑通了黄金路线，成功拦截了包含 SQL 注入和危险命名的代码。

```text
🚨🚨🚨 [Gemini Guard] 提交被中止！🚨🚨🚨
AI 检测到潜在的语义冲突或风险：
----------------------------------------
[警告]
1. **安全风险 (SQL注入)**: `connect_to_db` 函数通过直接拼接字符串构建SQL查询...
2. **语义冲突**: `delete_everything` 函数的命名具有极高的风险...
----------------------------------------
````

### V2 成果：上下文感知 (Context Awareness) 🌟

这是 V2 的核心升级。AI 不再只看 Diff，而是结合**完整文件内容**进行分析。
**案例：** 我们故意写错了一个变量名 (`MAX_RETRY` vs `MAX_RETRIES`)。

  * **旧版 (V1)**：会放行，因为它不知道 `MAX_RETRIES` 是否存在。
  * **新版 (V2)**：成功拦截！因为它读取了文件头部定义，发现了上下文冲突。

<!-- end list -->

```text
🚨🚨🚨 [Gemini Guard V2] 提交被中止！🚨🚨🚨
AI 检测到潜在的上下文冲突：
----------------------------------------
[警告]
1. **逻辑一致性问题**: 新增的代码 `print(f"...{MAX_RETRY}")` 引用了未在上下文中定义的变量 `MAX_RETRY`。
2. **潜在 Bug**: 文件上下文中定义的常量是 `MAX_RETRIES` (复数形式)，而新增代码中错误使用了单数形式。这将导致 `NameError`。
----------------------------------------
```

-----

## 🚀 如何安装 (Manual Setup)

这是一个概念验证 (POC) 版本，适用于本地测试。

1.  **前提条件**

      * 安装 Node.js 和 Gemini CLI: `npm install -g @google/gemini-cli`
      * 设置 API Key (在 `.bash_profile` 中): `export GEMINI_API_KEY="YOUR_KEY"`

2.  **安装钩子**

      * 进入项目目录: `cd .git/hooks/`
      * 创建文件: `touch pre-commit` (无后缀)
      * 粘贴下方的 **核心脚本** 内容。

3.  **Windows 用户必读 (关键)**

      * **修复换行符**: Windows 创建的文件可能包含 CRLF，导致脚本报错。请在 Git Bash 中运行：
        `sed -i 's/\r$//' pre-commit`
      * **赋予权限**: `chmod +x pre-commit`

-----

## 💻 核心脚本 (V2 - Context Aware)

```sh
#!/bin/sh
echo "🤖 [Gemini Guard V2] 正在启动上下文语义分析..."

# 获取暂存区的 diff
STAGED_DIFF=$(git diff --staged)

# 如果没有改动，跳过
if [ -z "$STAGED_DIFF" ]; then
    echo "🤖 [Gemini Guard] 没有检测到代码改动。"
    exit 0
fi

# ==========================================
# V2 新增逻辑：构建上下文 (Context)
# ==========================================
FILE_CONTEXT=""
# 获取所有被修改的文件名 (过滤掉已删除的文件 'd')
CHANGED_FILES=$(git diff --staged --name-only --diff-filter=d)

for file in $CHANGED_FILES; do
    # 简单的检查：确保文件存在且是文本文件
    if [ -f "$file" ]; then
        echo "   📄 正在读取上下文: $file ..."
        # 将文件名和内容追加到上下文变量中
        FILE_CONTEXT="$FILE_CONTEXT\n\n--- START OF FILE: $file ---\n"
        # 读取文件内容
        CONTENT=$(cat "$file")
        FILE_CONTEXT="$FILE_CONTEXT\n$CONTENT\n"
        FILE_CONTEXT="$FILE_CONTEXT\n--- END OF FILE: $file ---\n"
    fi
done

# ==========================================
# 核心 Prompt (V2)
# ==========================================
PROMPT="""
你是一个资深 Google 软件架构师。请分析以下代码提交。

【1. 代码变更 (Diff)】
这是我本次修改的具体内容：
---
$STAGED_DIFF
---

【2. 完整文件上下文 (Context)】
为了帮助你理解修改的影响，这是相关文件的完整内容：
---
$FILE_CONTEXT
---

【3. 分析任务】
请结合 diff 和 完整上下文，分析：
1. **逻辑一致性**：新增的代码是否使用了上下文中未定义的变量或函数？
2. **破坏性变更**：修改是否破坏了原文件中现有的类结构或函数逻辑？
3. **潜在 Bug**：是否存在仅看 diff 无法发现，但结合上下文就能发现的错误（如类型不匹配、作用域错误）？

【4. 回答格式】
* 如果**没有问题**，只回答：**[通过]**
* 如果**有问题**，以 **[警告]** 开头，详细解释原因。
"""

# ==========================================
# 调用 Gemini CLI
# ==========================================
ANALYSIS_RESULT=$(echo "$PROMPT" | gemini)

# 检查结果
if echo "$ANALYSIS_RESULT" | grep -q "\[警告\]"; then
    echo ""
    echo "🚨🚨🚨 [Gemini Guard V2] 提交被中止！🚨🚨🚨"
    echo "AI 检测到潜在的上下文冲突："
    echo "----------------------------------------"
    echo "$ANALYSIS_RESULT"
    echo "----------------------------------------"
    exit 1
else
    echo "✅ [Gemini Guard V2] 上下文分析通过。正在提交..."
    exit 0
fi
```

-----

## 🔮 下一步计划 (Roadmap)

此 Shell 版本已完成历史使命。为了更好的跨平台兼容性、更复杂的 AST 分析以及更简单的安装体验，我们将开启 **V3 重构**：

  * **Python 重构**: 抛弃 Shell 脚本，使用 Python 重写核心逻辑。
  * **AST 静态分析**: 智能识别 import 依赖，不仅仅读取当前文件，还能读取被引用的文件。
  * **一键安装**: `pip install gemini-guard`。

*(Current status: Tagged v1.0-shell-poc)*
