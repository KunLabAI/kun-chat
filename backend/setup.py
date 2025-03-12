import sys
import subprocess
import os

def install_dependencies():
    """安装requirements.txt中的所有依赖"""
    print("正在安装项目依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖安装完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
        return False

if __name__ == "__main__":
    # 安装依赖
    if install_dependencies():
        # 安装成功后启动主程序
        print("正在启动应用...")
        os.system(f"{sys.executable} main.py")
    else:
        print("由于依赖安装失败，无法启动应用")