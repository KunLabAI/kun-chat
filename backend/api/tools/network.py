from fastapi import APIRouter, Depends, HTTPException
import socket
import logging
import os
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/network", tags=["network"])

# 默认前端端口
DEFAULT_FRONTEND_PORT = 5173

# 从环境变量获取前端端口，如果未设置则使用默认值
def get_frontend_port():
    """获取前端端口"""
    try:
        # 尝试从环境变量获取
        frontend_port = os.environ.get("FRONTEND_PORT")
        if frontend_port and frontend_port.isdigit():
            return int(frontend_port)
        return DEFAULT_FRONTEND_PORT
    except Exception:
        return DEFAULT_FRONTEND_PORT

def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        # 创建一个UDP套接字
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接到一个外部地址，实际上不发送数据
        s.connect(("8.8.8.8", 80))
        # 获取分配的IP地址
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # 如果获取失败，返回本地回环地址
        return "127.0.0.1"

def get_all_network_interfaces():
    """获取所有网络接口地址"""
    interfaces = []
    try:
        # 获取所有网络接口
        hostname = socket.gethostname()
        # 获取本机IP
        local_ip = get_local_ip()
        # 获取前端端口
        frontend_port = get_frontend_port()
        
        # 添加本地回环地址
        interfaces.append({
            "name": "本地回环",
            "address": f"127.0.0.1:{frontend_port}"
        })
        
        # 添加局域网IP
        if local_ip != "127.0.0.1":
            interfaces.append({
                "name": "局域网",
                "address": f"{local_ip}:{frontend_port}"
            })
            
        # 尝试获取主机名对应的IP
        try:
            host_ip = socket.gethostbyname(hostname)
            if host_ip != "127.0.0.1" and host_ip != local_ip:
                interfaces.append({
                    "name": f"主机名({hostname})",
                    "address": f"{host_ip}:{frontend_port}"
                })
        except Exception:
            pass
            
    except Exception as e:
        logging.error(f"获取网络接口失败: {e}")
        # 至少返回本地回环地址
        frontend_port = get_frontend_port()
        interfaces.append({
            "name": "本地回环",
            "address": f"127.0.0.1:{frontend_port}"
        })
    
    return interfaces

# 全局变量，存储LAN访问状态
_lan_access_enabled = True

@router.get("/settings")
async def get_network_settings():
    """获取网络设置，包括LAN访问状态和应用URL"""
    local_ip = get_local_ip()
    frontend_port = get_frontend_port()
    
    # 构建应用URL
    app_url = f"http://localhost:{frontend_port}"
    
    # 构建局域网URL列表
    lan_urls = []
    if local_ip != "127.0.0.1":
        lan_urls.append(f"http://{local_ip}:{frontend_port}")
    
    return {
        "lanAccess": _lan_access_enabled,
        "lanAccessStatus": _lan_access_enabled,  # 实际状态，可能与设置不同
        "appUrl": app_url,
        "lanUrls": lan_urls
    }

@router.post("/lan-access")
async def update_lan_access(data: dict):
    """更新LAN访问设置"""
    global _lan_access_enabled
    
    # 从请求体中获取 enabled 参数
    if "enabled" not in data:
        raise HTTPException(status_code=422, detail="Missing 'enabled' parameter")
    
    _lan_access_enabled = data["enabled"]
    
    # 这里可以添加实际的网络配置更改
    # 例如修改防火墙规则等
    
    return {
        "success": True,
        "message": "LAN访问设置已更新"
    }

@router.get("/lan-urls")
async def get_lan_urls():
    """获取局域网URL列表"""
    local_ip = get_local_ip()
    frontend_port = get_frontend_port()
    
    lan_urls = []
    if local_ip != "127.0.0.1":
        lan_urls.append(f"http://{local_ip}:{frontend_port}")
    
    return {
        "urls": lan_urls,
        "status": _lan_access_enabled
    }

@router.get("/interfaces")
async def get_interfaces():
    """获取所有网络接口地址"""
    interfaces = get_all_network_interfaces()
    
    return {
        "interfaces": interfaces
    }
