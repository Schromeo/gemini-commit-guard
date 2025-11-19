
[简体中文](./README_CN.md) | English

# Gemini Commit Guard - Shell POC (V1 & V2)

A smart Git pre-commit hook powered by Google's Gemini CLI. It acts as an AI architect, performing semantic analysis on your code during `git commit` to intercept potential bugs before they pollute the codebase.

## 💡 Motivation

**The Traditional Workflow:** `git add` -> `git commit` -> `git push`.
**The Result:** The code compiles, but logical bugs or semantic conflicts slip through, polluting the main branch.
**The Aftermath:** Reverting commits, debugging locally, wasting time. It's boring and inefficient.

**The Solution:** This hook triggers an AI semantic analysis automatically when you commit. It catches "invisible" bugs (like variable typos across context) before they are even committed. It keeps the codebase clean and makes the boss happy.

## 🏆 Achievements

### V1: Dangerous Code Interception (Diff Analysis)
Validated the critical path. The hook successfully blocked code containing SQL injection vulnerabilities and risky naming conventions.

```text
🚨🚨🚨 [Gemini Guard] Commit Aborted! 🚨🚨🚨
AI detected potential semantic conflicts or risks:
----------------------------------------
[WARNING]
1. **Security Risk (SQL Injection)**: The `connect_to_db` function constructs SQL queries...
2. **Semantic Conflict**: The `delete_everything` function name implies high risk...
----------------------------------------
````

### V2: Context Awareness 🌟

This is the core upgrade. The AI no longer looks at just the `diff`; it reads the **full file context**.
**Case Study:** We introduced a typo: `MAX_RETRY` (undefined) vs `MAX_RETRIES` (defined in file header).

  * **Old (V1)**: Passed (Because it didn't know if `MAX_RETRY` existed elsewhere).
  * **New (V2)**: **Blocked\!** It read the context, realized the constant was plural, and flagged the typo.

<!-- end list -->

```text
🚨🚨🚨 [Gemini Guard V2] Commit Aborted! 🚨🚨🚨
AI detected potential context conflicts:
----------------------------------------
[WARNING]
1. **Logical Consistency**: The new code references `MAX_RETRY`, which is undefined in the context.
2. **Potential Bug**: The constant defined in the file context is `MAX_RETRIES` (plural), but the usage is singular. This will cause a `NameError`.
----------------------------------------
```

-----

## 🚀 Installation (Manual POC)

This is a Proof of Concept (POC) version for local testing.

1.  **Prerequisites**

      * Node.js & Gemini CLI: `npm install -g @google/gemini-cli`
      * Set API Key (in `.bash_profile`): `export GEMINI_API_KEY="YOUR_KEY"`

2.  **Setup Hook**
    * Navigate to project root.
    * Copy the script to your git hooks directory:
        ```bash
        cp hooks/pre-commit-script.sh .git/hooks/pre-commit
        ```
    * Make it executable:
        ```bash
        chmod +x .git/hooks/pre-commit
        ```

3.  **Windows Users (Critical)**

      * **Fix Line Endings**: Windows creates CRLF by default, which breaks `sh` scripts. Run this in Git Bash:
        `sed -i 's/\r$//' pre-commit`
      * **Permissions**: `chmod +x pre-commit`

-----

## 💻 Core Script

The core logic is located in [`hooks/pre-commit-script.sh`](./hooks/pre-commit-script.sh).

You can view the source code directly in the repository. It handles:
1.  **Diff Extraction**: Gets staged changes.
2.  **Context Building**: Reads full content of modified files.
3.  **Prompt Engineering**: Constructs a structured prompt for the AI.
4.  **Gemini Integration**: Calls the CLI and parses the result.

-----

## 🔮 Roadmap (V3)

This Shell version has served its purpose. For better cross-platform compatibility and advanced AST analysis, we are starting **V3 Refactoring**:

  * **Python Rewrite**: Replace Shell script with a robust Python CLI.
  * **AST Static Analysis**: Smarter context gathering (identifying imports and dependencies).
  * **Easy Installation**: `pip install gemini-guard`.

*(Current status: Tagged v1.0-shell-poc)*
