
[简体中文](./README_CN.md) | English

# Gemini Commit Guard - Python Refactor (V3)

An enterprise-grade Git pre-commit hook powered by **Google Gemini 2.0 Flash**. It acts as an AI architect, performing semantic analysis and static checks on your code during `git commit` to intercept potential bugs before they pollute the codebase.

> **Evolution:**
> * **V1/V2 (Legacy)**: Shell script + Node.js CLI (Tagged `v1.0-shell-poc`)
> * **V3 (Current)**: Pure Python + Official Google SDK + Virtual Environment

## 💡 Why Python?

While V1 proved the concept, V3 brings engineering maturity:
* **Architecture**: Modular design (`GitClient`, `AIEngine`, `Main`).
* **Robustness**: Python's `subprocess` handles Git output and encoding far better than Shell scripts.
* **Speed**: Uses the latest `gemini-2.0-flash` model via the official Python SDK.
* **Isolation**: Runs in a dedicated virtual environment (`venv`), keeping your global namespace clean.

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

*(Note: The `pre-commit` shim automatically activates the `venv` before running the Python logic.)*

-----

## 🏗️ Architecture

The project follows a clean, modular structure:

```text
gemini-guard/
├── src/
│   ├── main.py          # Entry point & Logic Handler
│   ├── git_client.py    # Handles git diff & context extraction
│   └── ai_engine.py     # Wraps Google Generative AI SDK
├── venv/                # Isolated Python Environment
├── requirements.txt     # Dependency lock file
└── pre-commit           # Shell Shim (The bridge between Git and Python)
```

## 💻 Usage

Just commit as usual\!

```bash
git add .
git commit -m "My awesome feature"
```

  * **If code is safe**: `[PASS]` -\> Commit succeeds.
  * **If bugs found**: `[WARNING]` -\> Commit blocked. You will see the AI's analysis in the terminal.

-----

## 🧪 Verified Capabilities

  * **SQL Injection Detection**: Catches dangerous string concatenations in SQL queries.
  * **Context Awareness**: Identifies typos in variable names by reading the full file context (e.g., `MAX_RETRY` vs `MAX_RETRIES`).
  * **Logical Consistency**: Ensures new code aligns with existing class definitions.

