import re
import logging
from typing import Tuple, Optional, Set
from ollama import OllamaClient
from config import API_CONFIG

logger = logging.getLogger(__name__)

# 常量定义
VALID_INSTRUCTIONS: Set[str] = {
    'FROM', 'PARAMETER', 'TEMPLATE', 'SYSTEM', 
    'ADAPTER', 'LICENSE', 'MESSAGE'
}

REQUIRED_INSTRUCTIONS: Set[str] = {'FROM'}

# 自定义错误类
class ModelError(Exception):
    """模型操作相关错误的基类"""
    pass

class ModelFileError(ModelError):
    """Modelfile 相关错误"""
    pass

class ModelCreateError(ModelError):
    """模型创建错误"""
    pass

class ModelAPIError(ModelError):
    """Ollama API 错误"""
    pass

async def validate_model_name(model_name: str) -> bool:
    """验证模型名称是否有效"""
    # 检查模型名称格式
    if not re.match(r'^[\w.-]+(/[\w.-]+)?(:\w+)?$', model_name):
        return False
        
    # 检查模型是否在已知列表中
    try:
        async with OllamaClient(API_CONFIG["OLLAMA_BASE_URL"]) as client:
            response = await client.show_model(model_name)
            return bool(response)
    except:
        # 如果模型不存在，show_model 可能会失败，这是正常的
        return True

async def validate_modelfile(content: str) -> Tuple[bool, Optional[str]]:
    """验证 Modelfile 的内容"""
    try:
        # 分割成行并移除注释和空行
        lines = []
        in_block = False
        block_content = []
        current_instruction = None
        
        # 确保 FROM 指令格式正确
        from_line = None
        for line in content.split('\n'):
            if line.startswith('FROM'):
                from_line = line
                break
                
        if not from_line:
            return False, "缺少 FROM 指令"
            
        # 验证 FROM 指令格式
        from_parts = from_line.split()
        if len(from_parts) != 2:
            return False, "FROM 指令格式错误，应为 'FROM model:tag'"
        if ':' not in from_parts[1]:
            return False, "FROM 指令格式错误，模型名称应包含标签，如 'model:tag'"
            
        for line in content.split('\n'):
            # 移除注释
            line = re.sub(r'#.*$', '', line).strip()
            if not line:
                continue
                
            # 处理多行块
            if line.endswith('<<EOF'):
                in_block = True
                block_content = []
                continue
            elif line == 'EOF':
                in_block = False
                if current_instruction:
                    lines.append(f"{current_instruction} {' '.join(block_content)}")
                continue
                
            if in_block:
                block_content.append(line)
                continue
                
            # 处理普通指令
            if any(line.startswith(instr) for instr in VALID_INSTRUCTIONS):
                # 找到匹配的指令
                for instr in VALID_INSTRUCTIONS:
                    if line.startswith(instr):
                        current_instruction = instr
                        # 将整行添加到 lines 中，保留原始格式
                        lines.append(line)
                        break
            else:
                # 检查是否是指令的一部分
                if current_instruction and not any(line.startswith(instr) for instr in VALID_INSTRUCTIONS):
                    # 如果不是新指令，就当作当前指令的继续内容
                    lines[-1] = f"{lines[-1]}\n{line}"
                else:
                    # 如果不是任何已知指令的开始，报错
                    return False, f"无效的指令行: {line}"
                    
        # 检查是否包含所有必需的指令
        found_instructions = set()
        for line in lines:
            for instr in VALID_INSTRUCTIONS:
                if line.startswith(instr):
                    found_instructions.add(instr)
                    break
                    
        missing = REQUIRED_INSTRUCTIONS - found_instructions
        if missing:
            return False, f"缺少必需的指令: {', '.join(missing)}"
            
        return True, None
        
    except Exception as e:
        return False, f"验证Modelfile时出错: {str(e)}"

async def safe_show_model(client: OllamaClient, model_name: str) -> bool:
    """安全地检查模型是否存在"""
    try:
        response = await client.show_model(model_name)
        return bool(response)
    except:
        return False

async def wait_for_model_creation(
    client: OllamaClient,
    model_name: str,
    max_retries: int = 30,  
    retry_delay: float = 10.0  
) -> bool:
    """等待并验证模型创建是否成功
    
    Args:
        client: OllamaClient实例
        model_name: 模型名称
        max_retries: 最大重试次数
        retry_delay: 每次重试之间的延迟（秒）
        
    Returns:
        bool: 模型是否创建成功
    """
    import asyncio
    
    logger.info(f"等待模型 {model_name} 创建完成...")
    for i in range(max_retries):
        logger.info(f"第 {i+1}/{max_retries} 次检查模型状态")
        if await safe_show_model(client, model_name):
            logger.info(f"模型 {model_name} 创建成功")
            return True
        logger.info(f"模型尚未就绪，等待 {retry_delay} 秒后重试...")
        await asyncio.sleep(retry_delay)
    
    logger.error(f"模型 {model_name} 创建超时，已达到最大重试次数 {max_retries}")
    return False

def convert_model_name(display_name: str) -> str:
    """
    将用户友好的模型名称转换为 Ollama 兼容的名称
    
    Args:
        display_name: 用户定义的模型名称，可以包含中文、标点等
        
    Returns:
        str: Ollama 兼容的模型名称（只包含字母、数字、连字符和下划线）
    """
    import re
    from hashlib import md5
    
    # 移除不支持的字符，只保留字母、数字、连字符和下划线
    safe_name = re.sub(r'[^\w\-]', '_', display_name)
    
    # 对所有自定义模型名称添加哈希值，避免与基础模型冲突
    # 使用 MD5 哈希，取前8位作为后缀
    name_hash = md5(display_name.encode('utf-8')).hexdigest()[:8]
    safe_name = f"custom_{name_hash}"
    
    # 如果需要在名称中包含原始名称的部分信息，可以使用下面的代码
    # 获取原始名称的安全版本（只保留合法字符）
    # original_safe = re.sub(r'[^\w\-]', '_', display_name)
    # 截取前10个字符，避免名称过长
    # original_safe = original_safe[:10].lower()
    # safe_name = f"custom_{original_safe}_{name_hash}"
    
    return safe_name.lower()
