import subprocess
import signal
import sys
import os
import time
import psutil
import socket
import argparse

def get_local_ip():
    """获取局域网IP地址"""
    try:
        # 创建一个UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接一个外部地址（不需要真实连接）
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass

class DevServer:
    def __init__(self, host=None):
        self.backend_process = None
        self.frontend_process = None
        self.host = host or get_local_ip()
        self.setup_signal_handlers()
        print(f"使用IP地址: {self.host}")

    def setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        print("\nShutting down development servers...")
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        if self.backend_process:
            kill_process_tree(self.backend_process.pid)
        if self.frontend_process:
            kill_process_tree(self.frontend_process.pid)

    def start_backend(self):
        print("Starting backend server...")
        backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))
        self.backend_process = subprocess.Popen(
            ["python", "main.py", "--host", self.host],
            cwd=backend_dir,
            env=env,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )

    def check_nodejs(self):
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("\n错误: 未检测到Node.js!")
            print("请按照以下步骤安装Node.js:")
            print("1. 访问 https://nodejs.org/")
            print("2. 下载并安装最新的LTS版本")
            print("3. 安装完成后重启终端")
            print("4. 重新运行此脚本\n")
            return False

    def start_frontend(self):
        print("Starting frontend development server...")
        if not self.check_nodejs():
            self.cleanup()
            sys.exit(1)
            
        frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
        
        # 检查node_modules是否存在
        if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
            print("Installing frontend dependencies...")
            try:
                subprocess.run("npm install", cwd=frontend_dir, shell=True, check=True)
                print("Frontend dependencies installed successfully!")
            except subprocess.CalledProcessError as e:
                print(f"Error installing frontend dependencies: {e}")
                raise
        
        try:
            # 使用shell=True来运行npm命令
            self.frontend_process = subprocess.Popen(
                "npm run dev",
                cwd=frontend_dir,
                shell=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            print("Frontend server started successfully!")
        except Exception as e:
            print(f"Error starting frontend server: {e}")
            raise

    def run(self):
        try:
            self.start_backend()
            time.sleep(2)  # 给后端一些启动时间
            self.start_frontend()
            print("\nDevelopment servers are running!")
            print("Press Ctrl+C to stop all servers")
            
            # 保持脚本运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.cleanup()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.cleanup()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="运行开发服务器")
    parser.add_argument("--host", help="指定主机IP地址，默认自动检测", default=None)
    args = parser.parse_args()
    
    server = DevServer(host=args.host)
    server.run()
