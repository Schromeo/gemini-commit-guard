[简体中文](./README_CN.md) | English

# Gemini Commit Guard - Python Refactor (V3.5)

An enterprise-grade Git pre-commit hook powered by **Google Gemini 2.0 Flash**. It acts as an AI architect, performing semantic analysis and static checks on your code during `git commit` to intercept potential bugs before they pollute the codebase.

## 💡 Why Build This?

**The Problem:** Traditional workflows (`git commit` -> `CI/CD`) are reactive. Bugs are caught *after* they enter the codebase, leading to messy revert commits and broken builds.
**The Solution:** A proactive AI guard. By hooking into the commit process, we can use LLMs to "understand" the change in the context of the full file, catching invisible logic errors (like variable typos across scopes) that linters miss.

## 📜 Development Log (The Journey)

This project evolved from a simple script to a robust engineering tool. Here is the path we took:

### Phase 1: The Shell POC (V1 & V2)
* **Goal**: Prove that `git diff` could be piped to Gemini CLI to stop a commit.
* **Challenge**: Windows `CRLF` line endings and `BOM` encoding broke the Shell script repeatedly.
* **Breakthrough**: V2 introduced **Context Awareness**. Instead of just sending the `diff`, we read the full file content. This allowed the AI to detect that `MAX_RETRY` (typo) did not match `MAX_RETRIES` (defined at the top of the file).

### Phase 2: The Python Refactor (V3)
* **Goal**: Solve cross-platform issues and improve architecture.
* **Solution**: Re-wrote the core logic in Python using `subprocess` for Git operations and the official Google SDK (`google-generativeai`) for API calls.
* **Architecture**: Implemented a modular design with `GitClient` (Data Layer), `AIEngine` (Service Layer), and `Main` (Controller).

### Phase 3: The "Talkative AI" Incident (V3.5)
* **The Bug**: The AI was *too* helpful. When reviewing the code, it wrote a long essay praising the refactoring. However, the essay contained the word `[WARNING]` (quoting our own code), which triggered our regex parser and blocked a valid commit!
* **The Fix**: We moved from simple String Matching to **Structured JSON Output**.
* **Implementation**: We utilized the **Native JSON Mode** (`response_mime_type="application/json"`) in Gemini 1.5/2.0 models to force the AI to return a strict JSON object, ensuring deterministic parsing.

---

## 🚀 Installation

### 1. Prerequisites
* Python 3.8+
* Git
* A Google Gemini API Key ([Get it here](https://aistudio.google.com/app/apikey))

### 2. Setup (One-time)

Run these commands in your project root:

```bash
# 1. Create Virtual Environment
python -m venv venv

# 2. Install Dependencies
# (Windows: venv/Scripts/activate, Mac/Linux: source venv/bin/activate)
source venv/Scripts/activate
pip install google-generativeai
pip freeze > requirements.txt

# 3. Configure API Key (Add to your ~/.bash_profile or Environment Variables)
export GEMINI_API_KEY="YOUR_API_KEY_HERE"
````

### 3\. Install the Hook

We use a shell shim to bridge Git and Python. Run this to overwrite your current hook:

```bash
# Copy the shim script
cp pre-commit .git/hooks/pre-commit

# Make it executable
chmod +x .git/hooks/pre-commit
```

-----

## 🏗️ Architecture

```text
gemini-guard/
├── src/
│   ├── main.py          # Logic Controller & JSON Parser
│   ├── git_client.py    # Git Operations (Diff & Context)
│   └── ai_engine.py     # Gemini SDK Wrapper (Native JSON Mode)
├── venv/                # Isolated Environment
├── pre-commit           # Shell Shim
└── requirements.txt     # Dependencies
```

## 🧪 Capabilities

  * **SQL Injection Detection**: Identifies dangerous string concatenations.
  * **Context-Aware Typo Detection**: Reads full files to verify variable definitions.
  * **Robust JSON Parsing**: immune to "prompt injection" or verbose AI responses.
