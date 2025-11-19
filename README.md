[简体中文](./README_CN.md) | English

# Gemini Commit Guard - The DevOps Platform (V4)

An enterprise-grade, full-stack **AI Audit Platform** for Git commits. Powered by **Google Gemini 2.0 Flash**, it acts as an AI architect that not only intercepts potential bugs during `git commit` but also provides a **Visual Dashboard** for observability and history tracking.

## 💡 Why Build This?

**The Problem:** Traditional workflows (`git commit` -> `CI/CD`) are reactive. Bugs are caught *after* they enter the codebase. Furthermore, terminal errors are ephemeral; once you close the window, the feedback is lost.
**The Solution:** A closed-loop system.
1.  **Proactive Guard**: Hooks into the commit process to catch invisible logic errors (like variable typos across scopes) using context-aware AI.
2.  **Observability**: Persists every analysis result to a local database and visualizes it in a dashboard.

## 📜 Development Log (The Journey)

This project evolved from a simple script to a robust engineering platform. Here is the path we took:

### Phase 1: The Shell POC (V1 & V2)
* **Goal**: Prove that `git diff` could be piped to Gemini CLI to stop a commit.
* **Challenge**: Windows `CRLF` line endings and `BOM` encoding broke the Shell script repeatedly.
* **Breakthrough**: V2 introduced **Context Awareness**. Instead of just sending the `diff`, we read the full file content.

### Phase 2: The Python Refactor (V3)
* **Goal**: Solve cross-platform issues and improve architecture.
* **Solution**: Re-wrote the core logic in Python using `subprocess` for Git operations and the official Google SDK (`google-generativeai`).
* **Architecture**: Modular design with `GitClient`, `AIEngine`, and `Main`.

### Phase 3: The "Talkative AI" Incident (V3.5)
* **The Bug**: The AI was *too* helpful. It wrote long essays praising the code, but the essay quoted our `[WARNING]` trigger, causing the parser to self-block!
* **The Fix**: We moved to **Native JSON Mode** (`response_mime_type="application/json"`) in Gemini 2.0, forcing strict JSON output for deterministic parsing.

### Phase 4: Full-Stack Observability (V4) 🚀
* **Goal**: "Don't just block it, record it."
* **Implementation**: Introduced **SQLite** for local persistence and **Streamlit** for visualization.
* **Result**: Built a dashboard to track Pass/Fail metrics and review detailed AI logs side-by-side with code diffs.

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

# 2. Activate & Install Dependencies
# (Windows: venv/Scripts/activate, Mac/Linux: source venv/bin/activate)
source venv/Scripts/activate

# Install SDK + Dashboard tools
pip install google-generativeai streamlit pandas
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

## 📊 Usage & Dashboard

### 1\. The Auto-Guard (Terminal)

Just commit as usual. The hook runs automatically in the background.

```bash
git commit -m "Refactor logic"
```

  * **If Safe**: Commit proceeds.
  * **If Risky**: Commit is blocked with a red alert.
  * **Logs**: Every attempt is saved to `.gemini_audit.db`.

### 2\. The Visual Dashboard (GUI) 🆕

To audit your project history and view detailed AI reports:

```bash
streamlit run src/dashboard.py
```

This opens a web interface in your browser featuring:

  * 📈 **Live Metrics**: Track your Commit Pass Rate on the sidebar.
  * 📜 **Audit History**: A timeline of every commit attempt (PASS/FAIL).
  * 🔍 **Deep Dive**: Click on any record to compare the **Git Diff** side-by-side with the **AI's JSON analysis**.

-----

## 🏗️ Architecture

```text
gemini-guard/
├── src/
│   ├── main.py          # Logic Controller
│   ├── git_client.py    # Git Operations
│   ├── ai_engine.py     # Gemini SDK (JSON Mode)
│   ├── audit_logger.py  # SQLite Manager (Persistence)
│   └── dashboard.py     # Streamlit Web App (Visualization)
├── venv/                # Isolated Environment
├── .gemini_audit.db     # Local Database
└── pre-commit           # Shell Shim
```

## 🧪 Capabilities

  * **SQL Injection Defense**: Identifies dangerous string concatenations.
  * **Context-Awareness**: Reads full files to verify variable definitions and scope.
  * **Robust JSON Parsing**: Immune to "prompt injection" or verbose AI responses.
  * **Full History Audit**: Never lose track of a security warning.

-----

## 🔮 Product Roadmap: The Road to V5

We are transitioning Gemini Guard from a "Python Tool" to a **"Standalone DevOps Product"**.

### 🔜 Milestone 1: Centralized Intelligence (V4.5)

  * **Global Database**: Move storage to `~/.gemini-guard/` to act as a central hub for all your projects.
  * **Multi-Project Support**: Isolate audit logs by project path. Manage 10+ repositories in a single Dashboard.

### 🔜 Milestone 2: Zero-Dependency (V5)

  * **Binary Distribution**: Package the entire tool (Python + Streamlit + SDK) into a single `.exe` or binary file using **PyInstaller**.
  * **Target Audience**: Enable Frontend/Java/Go developers to use Gemini Guard without installing Python or Pip.

### 🔜 Milestone 3: The "One-Click" Experience

  * **`gg init`**: A new CLI command to automatically detect the repo, install hooks, and register the project in the global database.
  * **Unified Dashboard**: A switchable interface to monitor the health of all your active projects in one view.
