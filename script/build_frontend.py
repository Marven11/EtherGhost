#!/usr/bin/env python3
"""
构建前端脚本

在poetry build前自动运行此脚本构建前端
"""

import subprocess
import sys
import os

def build_frontend() -> int:
    """运行前端构建脚本"""
    print("构建前端...")
    script_path = os.path.join(os.path.dirname(__file__), "build.sh")
    
    try:
        result = subprocess.run(["bash", script_path], 
                              capture_output=True, 
                              text=True,
                              cwd=os.path.dirname(os.path.dirname(__file__)))
        print(result.stdout)
        if result.stderr:
            print(f"警告: {result.stderr}", file=sys.stderr)
        
        if result.returncode != 0:
            print(f"构建失败，退出码: {result.returncode}", file=sys.stderr)
            return result.returncode
            
        print("前端构建完成!")
        return 0
    except FileNotFoundError:
        print(f"错误: 找不到构建脚本 {script_path}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(build_frontend())
