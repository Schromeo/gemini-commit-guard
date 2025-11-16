
# Gemini Commit Guard - V1 (Proof of Concept)

这是一个基于 Google Gemini CLI 的智能 Git pre-commit 钩子，它可以在你 `git commit` 时对你的代码进行“语义分析”，防止潜在的 Bug 被提交。

## 灵感来源 (The "Why")

传统的开发流程：`git add .` -> `git commit` -> `git push`。
结果：编译成功，但 push 之后污染了代码库，因为有隐形的语义 Bug。
接下来：回退代码 (revert)，本地疯狂找 Bug，好无趣，好无聊。

而这个工具可以在 `commit` 指令被触发时，自动调用 Gemini 进行语义分析，在 Bug 进入代码库**之前**就将其拦截。好好玩，老板再也不担心潜在的 Bug 污染代码库了！

## V1 (POC) 成果

我们成功跑通了 "git commit -> 触发脚本 -> Gemini API 分析 -> 成功拦截危险提交" 的黄金路线！

**成功拦截“危险代码”的证明：**
```bash
🚨🚨🚨 [Gemini Guard] 提交被中止！🚨🚨🚨
AI 检测到潜在的语义冲突或风险：
----------------------------------------
[警告]
本次代码变更引入了严重的安全漏洞和潜在的运行时错误。

1.  **安全风险 (SQL注入)**: `dangerous_code.py` 文件中的...
2.  **潜在的运行时错误**: `connect_to_db` 函数中使用了未定义的变量 `db`...
3.  **语义冲突与高风险函数**: `delete_everything` 函数的命名具有极高的风险...
----------------------------------------
请审查你的代码后再次尝试提交。
````

-----

## 🚀 如何安装和使用 (V1 手动版)

由于 V1 是一个概念验证 (POC)，它还不能自动安装。

1.  **安装 Gemini CLI**

    ```bash
    npm install -g @google/gemini-cli
    ```

2.  **获取并设置 API 密钥**

      * 从 [Google AI Studio](https://aistudio.google.com/app/apikey) 获取你的 API 密钥。
      * 在你的 `~/.bash_profile` (或 `~/.zshrc`) 中设置它：
        ```bash
        export GEMINI_API_KEY="YOUR_API_KEY_HERE"
        ```
      * **重要 (Windows 用户)**：确保你在 **Git Bash** 环境中设置了此密钥，因为 `sh` 脚本会在 Bash 环境中运行。

3.  **创建钩子脚本**

      * 在你的项目根目录，进入 `.git/hooks/` 文件夹。
      * 创建一个新文件，命名为 `pre-commit` (没有后缀名)。

4.  **复制 V1 脚本**

      * 将下面的**核心脚本**完整复制到你刚创建的 `pre-commit` 文件中。

5.  **解决 Windows 兼容性问题 (关键！)**

      * **修复换行符 (CRLF -\> LF)**：Windows 创建的文件默认使用 CRLF 换行符，这会导致 `sh` 脚本失败 (报 `No such file or directory` 错误)。你必须在 Git Bash 中运行 `sed` 来修复它：
        ```bash
        # 在 .git/hooks 目录中运行
        sed -i 's/\r$//' pre-commit
        ```
      * **修复 BOM 编码**：如果使用记事本保存，可能会添加 UTF-8 BOM，同样会导致脚本失败。推荐使用 VS Code 或在 Git Bash 中用 `cat <<'EOF' ... EOF` 来创建文件。
      * **添加执行权限**：
        ```bash
        chmod +x pre-commit
        ```

-----

## V1 核心脚本 (pre-commit)

```sh
#!/bin/sh
echo "🤖 [Gemini Guard] 正在启动语义分析..."

# 1. 获取所有暂存的 (staged) 代码改动
STAGED_DIFF=$(git diff --staged)

# 2. 如果没有改动，就跳过
if [ -z "$STAGED_DIFF" ]; then
    echo "🤖 [Gemini Guard] 没有检测到代码改动。"
    exit 0
fi

# ----------------------------------------------------
# 核心 Prompt - 我们在这里定义AI的角色和任务
# ----------------------------------------------------
PROMPT="""
你是一个资深的Google软件架构师，你的任务是分析代码变更并防止潜在的Bug。

这是我即将提交的代码改动（git diff格式）：
---
$STAGED_DIFF
---

请基于这份 diff，分析以下问题：
1. **语义冲突**：这个改动是否有可能与项目中的其他部分产生逻辑冲突或运行时Bug？
2. **潜在风险**：是否存在任何隐藏的风险、性能问题或未处理的边缘情况？

你的回答必须遵循以下格式：
* 如果**没有发现任何问题**，请只回答：**[通过]**
* 如果**发现任何问题或风险**，请以 **[警告]** 开头，然后详细说明你的担忧。
"""

# ----------------------------------------------------
# 调用 Gemini CLI 并分析结果
# ----------------------------------------------------
# 我们将 PROMPT 通过管道传给 gemini-cli
ANALYSIS_RESULT=$(echo "$PROMPT" | gemini)

# 关键：检查 AI 的输出是否包含 "[警告]"
if echo "$ANALYSIS_RESULT" | grep -q "\[警告\]"; then
    # 5. 发现问题：打印警告并中止提交
    echo ""
    echo "🚨🚨🚨 [Gemini Guard] 提交被中止！🚨🚨🚨"
    echo "AI 检测到潜在的语义冲突或风险："
    echo "----------------------------------------"
    echo "$ANALYSIS_RESULT"
    echo "----------------------------------------"
    echo "请审查你的代码后再次尝试提交。"
    exit 1 # <--- 非零退出，中止提交！
else
    # 6. 一切正常：允许提交
    echo "✅ [Gemini Guard] 语义分析通过。正在提交..."
    exit 0 # <--- 零退出，继续提交！
fi
```

-----

## 💡 未来规划 (V2/V3)

V1 证明了路线可行，但它还很简单。为了让它成为一个真正的工程工具，下一步的计划是：

  * **V2 (提升准确性 - Context Aware)**

      * **问题：** V1 只把 `diff` 发送给 AI，AI 看不到“全貌”，导致分析“不完备”。
      * **方案：** 进化脚本，使其在调用 AI 之前，能智能地分析 `diff`，并自动抓取所有**相关联**的本地文件（比如被调用的函数所在的源文件、`import` 的模块等），将它们**一起**作为“上下文 (Context)”发送给 `gemini-cli`，极大提高 AI 语义分析的准确性。

  * **V3 (工程化 - Team Ready)**

      * **问题：** `.git/hooks` 文件夹是本地的，无法被提交到 Git 仓库，团队其他人无法共享。
      * **方案：** 引入 **Husky** (NPM 包) 或 **Lefthook** (Go 工具) 这样的 Git 钩子管理器。这允许我们将 `pre-commit` 脚本作为项目的一部分（比如 `package.json` 里的一个命令）提交到仓库。团队成员只需 `npm install`，这个 AI 守卫就会**自动安装**到每个人的本地，真正赋能整个团队。

