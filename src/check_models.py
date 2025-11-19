import google.generativeai as genai
import os

# 获取 Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ No API Key found")
    exit()

genai.configure(api_key=api_key)

print("🔍 Checking available models for your API Key...")
print("------------------------------------------------")

try:
    # 列出所有模型
    for m in genai.list_models():
        # 我们只关心能生成内容(generateContent)的模型，不关心做嵌入(embedding)的模型
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Found: {m.name}")
            
except Exception as e:
    print(f"❌ Error listing models: {e}")

print("------------------------------------------------")