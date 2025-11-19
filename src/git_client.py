import subprocess
import os
from typing import List

class GitClient:
    def __init__(self):
        # 确保我们在一个 Git 仓库里
        if not os.path.exists(".git"):
            raise RuntimeError("Not a git repository (no .git folder found).")

    def _run_command(self, args: List[str]) -> str:
        """
        运行一个 Shell 命令并返回输出字符串
        """
        try:
            result = subprocess.check_output(args, stderr=subprocess.STDOUT)
            return result.decode("utf-8").strip()
        except subprocess.CalledProcessError as e:
            # 如果命令失败（比如 git 报错），返回空或抛出异常
            return ""
        except UnicodeDecodeError:
            # 如果输出包含无法解码的字符
            return "[Binary Output]"

    def get_staged_diff(self) -> str:
        """
        获取暂存区的 diff (git diff --staged)
        """
        return self._run_command(["git", "diff", "--staged"])

    def get_staged_files(self) -> List[str]:
        """
        获取暂存区的文件列表 (过滤掉已删除的文件)
        """
        output = self._run_command([
            "git", "diff", "--staged", "--name-only", "--diff-filter=d"
        ])
        if not output:
            return []
        return output.split("\n")

    def read_file_content(self, file_path: str) -> str:
        """
        读取文件内容 (用来构建上下文)
        """
        if not os.path.exists(file_path):
            return ""
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            return "[Binary File - Content Skipped]"
        except Exception as e:
            return f"[Error reading file: {str(e)}]"

# ==========================================
# 单元测试 (Self-Test)
# ==========================================
if __name__ == "__main__":
    print("🧪 Testing Git Client...")
    git = GitClient()
    
    print(f"📂 Staged Files: {git.get_staged_files()}")
    
    diff = git.get_staged_diff()
    # 只打印前100个字符，避免刷屏
    print(f"📝 Diff Preview: {diff[:100]}...")