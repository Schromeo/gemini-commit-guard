# 这是一个配置模块
CONFIG_VERSION = "1.0"
MAX_RETRIES = 3
TIMEOUT = 30

def connect():
    print("Connecting...")
    print(f"Max retries allowed: {MAX_RETRIES}")