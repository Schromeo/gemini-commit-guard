import os
import sys
import google.generativeai as genai
from google.generativeai.types import GenerationConfig # <--- 1. 新增导入

class AIEngine:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ Error: GEMINI_API_KEY environment variable not found.")
            sys.exit(1)
        
        try:
            genai.configure(api_key=api_key)
            # 使用最新的 Gemini 2.0 Flash
            self.model = genai.GenerativeModel('models/gemini-2.0-flash')
        except Exception as e:
            print(f"❌ Error configuring Google AI SDK: {e}")
            sys.exit(1)

    def analyze_code(self, diff: str, context: str = "") -> str:
        print("🤖 [Gemini Python] Thinking (JSON Mode)...", flush=True)
        
        # 简化后的 Prompt (既然强制了 JSON 模式，Prompt 可以简单点了)
        prompt = f"""
You are a Git Pre-commit Guard. 
Analyze the code changes.

[CODE DIFF]
{diff}

[FULL FILE CONTEXT]
{context}

[RESPONSE SCHEMA]
You MUST return a JSON object matching this schema:
{{
    "status": "PASS" or "FAIL",
    "message": "Short summary of findings",
    "details": ["Detail 1", "Detail 2"]
}}

Rules:
1. If code is safe -> status: "PASS", details: [].
2. If bugs/security risks found -> status: "FAIL".
"""
        try:
            # 2. 关键修改：强制开启 JSON 模式！
            response = self.model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            return response.text
        except Exception as e:
            # 如果出错，返回一个合法的 JSON 格式错误信息，防止 main.py 炸裂
            return f'{{"status": "FAIL", "message": "API Error: {str(e)}", "details": []}}'

if __name__ == "__main__":
    engine = AIEngine()
    # 测试一下
    print(engine.analyze_code("print('hello')", ""))