import sys
import json
import re
from git_client import GitClient
from ai_engine import AIEngine

def clean_json_string(json_str):
    """
    清理 AI 可能返回的 Markdown 格式，比如 ```json ... ```
    """
    # 去掉开头的 ```json 或 ```
    json_str = re.sub(r'^```json', '', json_str.strip())
    json_str = re.sub(r'^```', '', json_str.strip())
    # 去掉结尾的 ```
    json_str = re.sub(r'```$', '', json_str.strip())
    return json_str.strip()

def main():
    print("🤖 [Gemini Guard Python] Initializing...", flush=True)

    try:
        git = GitClient()
        ai = AIEngine()
    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        sys.exit(1)

    # 1. 获取 Diff
    diff = git.get_staged_diff()
    if not diff:
        print("✅ No staged changes detected. Skipping AI analysis.")
        sys.exit(0)

    print("   🔍 Reading file context...", flush=True)

    # 2. 构建上下文
    context_str = ""
    files = git.get_staged_files()
    for file_path in files:
        content = git.read_file_content(file_path)
        context_str += f"\n\n--- START OF FILE: {file_path} ---\n{content}\n--- END OF FILE: {file_path} ---\n"

    # 3. 调用 AI (获取 JSON 字符串)
    raw_result = ai.analyze_code(diff, context_str)

    # 4. 解析 JSON (这是 V3.5 的核心升级！)
    try:
        # 清理并解析
        cleaned_result = clean_json_string(raw_result)
        analysis_data = json.loads(cleaned_result)
        
        # 打印友好的分析报告
        print("\n" + "="*40)
        print(f"🤖 AI Status: {analysis_data.get('status')}")
        print(f"📝 Message:   {analysis_data.get('message')}")
        if analysis_data.get('details'):
            print("👇 Details:")
            for detail in analysis_data['details']:
                print(f"   - {detail}")
        print("="*40 + "\n")

        # 5. 根据 status 字段决定去留
        if analysis_data.get('status') == 'FAIL':
            print("🚨 Commit Aborted! Issues detected.")
            sys.exit(1)
        else:
            print("✅ Analysis Passed. Proceeding with commit...")
            sys.exit(0)

    except json.JSONDecodeError:
        # 如果 AI 没返回 JSON（极其罕见），我们要兜底
        print("\n❌ Error: AI did not return valid JSON.")
        print(f"Raw Output: {raw_result}")
        sys.exit(1)

if __name__ == "__main__":
    main()