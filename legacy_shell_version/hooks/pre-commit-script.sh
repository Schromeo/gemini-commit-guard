#!/bin/sh
echo "🤖 [Gemini Guard V2] Starting Contextual Semantic Analysis..."

# Get staged diff
STAGED_DIFF=$(git diff --staged)

# Skip if empty
if [ -z "$STAGED_DIFF" ]; then
    echo "🤖 [Gemini Guard] No changes detected."
    exit 0
fi

# ==========================================
# V2 Logic: Build Context
# ==========================================
FILE_CONTEXT=""
# Get list of changed files (exclude deleted)
CHANGED_FILES=$(git diff --staged --name-only --diff-filter=d)

for file in $CHANGED_FILES; do
    # Simple check: ensure file exists and is likely text
    if [ -f "$file" ]; then
        echo "   📄 Reading context: $file ..."
        FILE_CONTEXT="$FILE_CONTEXT\n\n--- START OF FILE: $file ---\n"
        CONTENT=$(cat "$file")
        FILE_CONTEXT="$FILE_CONTEXT\n$CONTENT\n"
        FILE_CONTEXT="$FILE_CONTEXT\n--- END OF FILE: $file ---\n"
    fi
done

# ==========================================
# Core Prompt (English Version)
# ==========================================
PROMPT="""
You are a Senior Software Architect at Google. Please analyze the following code commit.

[1. The Diff]
Here are the changes I am trying to commit:
---
$STAGED_DIFF
---

[2. Full File Context]
To help you understand the impact, here is the full content of the modified files:
---
$FILE_CONTEXT
---

[3. Analysis Task]
Combine the diff and the context to analyze:
1. **Logical Consistency**: Does the new code use variables/functions not defined in the context?
2. **Destructive Changes**: Does the change break existing class structures or logic?
3. **Potential Bugs**: Are there errors (like typos, scope issues) that are visible only with context?

[4. Response Format]
* If **No Issues**: Reply ONLY with: **[PASS]**
* If **Issues Found**: Start with **[WARNING]**, then explain the reason in detail.
"""

# ==========================================
# Call Gemini CLI
# ==========================================
ANALYSIS_RESULT=$(echo "$PROMPT" | gemini)

# Check result (Looking for [WARNING] tag)
# Note: We updated the grep logic to look for the English tag
if echo "$ANALYSIS_RESULT" | grep -q "\[WARNING\]"; then
    echo ""
    echo "🚨🚨🚨 [Gemini Guard V2] Commit Aborted! 🚨🚨🚨"
    echo "AI detected potential context conflicts:"
    echo "----------------------------------------"
    echo "$ANALYSIS_RESULT"
    echo "----------------------------------------"
    exit 1
else
    echo "✅ [Gemini Guard V2] Analysis Passed. Committing..."
    exit 0
fi
