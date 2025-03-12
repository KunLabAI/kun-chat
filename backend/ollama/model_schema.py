import json
from enum import Enum
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import logging
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class ModelParamCategory(Enum):
    ATTENTION = "attention"
    ARCHITECTURE = "architecture"
    TOKENIZER = "tokenizer"
    GENERAL = "general"
    GENERATION = "generation"

# 量化级别映射
QUANTIZATION_LEVELS = {
    'Q2_K': {
        'bits': 2,
        'description': '2-bit量化，适用于极限压缩场景'
    },
    'Q3_K_S': {
        'bits': 3,
        'description': '3-bit量化，小型模型优化'
    },
    'Q3_K_M': {
        'bits': 3,
        'description': '3-bit量化，中型模型优化'
    },
    'Q3_K_L': {
        'bits': 3,
        'description': '3-bit量化，大型模型优化'
    },
    'Q4_0': {
        'bits': 4,
        'description': '4-bit线性量化'
    },
    'Q4_K_S': {
        'bits': 4,
        'description': '4-bit量化，小型模型优化'
    },
    'Q4_K_M': {
        'bits': 4,
        'description': '4-bit量化，中型模型优化'
    },
    'Q5_0': {
        'bits': 5,
        'description': '5-bit线性量化'
    },
    'Q5_K_S': {
        'bits': 5,
        'description': '5-bit量化，小型模型优化'
    },
    'Q6_K': {
        'bits': 6,
        'description': '6-bit量化'
    },
    'Q8_0': {
        'bits': 8,
        'description': '8-bit线性量化'
    },
    'F16': {
        'bits': 16,
        'description': '16-bit浮点数'
    },
    'F32': {
        'bits': 32,
        'description': '32-bit浮点数'
    }
}

# 高级参数定义
MODEL_PARAM_SCHEMA = {
    # 注意力相关参数
    "attention.head_count": {
        "name": "注意力头数量",
        "category": ModelParamCategory.ATTENTION,
        "type": int,
        "unit": "个",
        "description": "模型中注意力头的数量"
    },
    "attention.head_count_kv": {
        "name": "KV注意力头数量",
        "category": ModelParamCategory.ATTENTION,
        "type": int,
        "unit": "个",
        "description": "KV缓存中的注意力头数量"
    },
    "attention.layer_norm_rms_epsilon": {
        "name": "层归一化epsilon",
        "category": ModelParamCategory.ATTENTION,
        "type": float,
        "unit": None,
        "description": "层归一化中的epsilon值"
    },
    "attention.rope_scaling": {
        "name": "RoPE缩放",
        "category": ModelParamCategory.ATTENTION,
        "type": float,
        "unit": None,
        "description": "RoPE位置编码的缩放因子"
    },

    # 架构相关参数
    "num_layers": {
        "name": "层数",
        "category": ModelParamCategory.ARCHITECTURE,
        "type": int,
        "unit": "层",
        "description": "模型的层数"
    },
    "num_attention_heads": {
        "name": "注意力头数",
        "category": ModelParamCategory.ARCHITECTURE,
        "type": int,
        "unit": "个",
        "description": "注意力头的数量"
    },
    "hidden_size": {
        "name": "隐藏层大小",
        "category": ModelParamCategory.ARCHITECTURE,
        "type": int,
        "unit": None,
        "description": "隐藏层的维度大小"
    },
    "intermediate_size": {
        "name": "中间层大小",
        "category": ModelParamCategory.ARCHITECTURE,
        "type": int,
        "unit": None,
        "description": "前馈网络中间层的维度大小"
    },
    "num_key_value_heads": {
        "name": "KV头数量",
        "category": ModelParamCategory.ARCHITECTURE,
        "type": int,
        "unit": "个",
        "description": "Key-Value注意力头的数量"
    },
    "num_hidden_layers": {
        "name": "隐藏层数量",
        "category": ModelParamCategory.ARCHITECTURE,
        "type": int,
        "unit": "层",
        "description": "模型中隐藏层的数量"
    },

    # 分词器相关参数
    "vocab_size": {
        "name": "词表大小",
        "category": ModelParamCategory.TOKENIZER,
        "type": int,
        "unit": "个词",
        "description": "分词器词表的大小"
    },
    "bos_token_id": {
        "name": "开始标记ID",
        "category": ModelParamCategory.TOKENIZER,
        "type": int,
        "unit": None,
        "description": "句子开始标记的ID"
    },
    "eos_token_id": {
        "name": "结束标记ID",
        "category": ModelParamCategory.TOKENIZER,
        "type": int,
        "unit": None,
        "description": "句子结束标记的ID"
    },
    "pad_token_id": {
        "name": "填充标记ID",
        "category": ModelParamCategory.TOKENIZER,
        "type": int,
        "unit": None,
        "description": "填充标记的ID"
    },
    "max_position_embeddings": {
        "name": "最大位置编码",
        "category": ModelParamCategory.TOKENIZER,
        "type": int,
        "unit": None,
        "description": "位置编码的最大长度"
    },

    # 生成相关参数
    "temperature": {
        "name": "温度",
        "category": ModelParamCategory.GENERATION,
        "type": float,
        "unit": None,
        "description": "生成时的温度参数，控制输出的随机性"
    },
    "top_p": {
        "name": "Top P",
        "category": ModelParamCategory.GENERATION,
        "type": float,
        "unit": None,
        "description": "核采样阈值，控制词的采样范围"
    },
    "top_k": {
        "name": "Top K",
        "category": ModelParamCategory.GENERATION,
        "type": int,
        "unit": None,
        "description": "选取概率最高的K个词进行采样"
    },
    "repeat_penalty": {
        "name": "重复惩罚",
        "category": ModelParamCategory.GENERATION,
        "type": float,
        "unit": None,
        "description": "重复词的惩罚系数"
    },
    "num_ctx": {
        "name": "上下文窗口",
        "category": ModelParamCategory.GENERATION,
        "type": int,
        "unit": "tokens",
        "description": "模型能处理的最大上下文长度"
    },
    "context_length": {
        "name": "上下文窗口",
        "category": ModelParamCategory.GENERATION,
        "type": int,
        "unit": "tokens",
        "description": "模型能处理的最大上下文长度"
    },

    # 通用参数
    "model_type": {
        "name": "模型类型",
        "category": ModelParamCategory.GENERAL,
        "type": str,
        "unit": None,
        "description": "模型的架构类型"
    },
    "rope_theta": {
        "name": "RoPE基频",
        "category": ModelParamCategory.GENERAL,
        "type": float,
        "unit": None,
        "description": "RoPE位置编码的基频"
    },
    "rope_scaling_type": {
        "name": "RoPE缩放类型",
        "category": ModelParamCategory.GENERAL,
        "type": str,
        "unit": None,
        "description": "RoPE位置编码的缩放类型"
    }
}

# 需要跳过的大型字段
SKIP_LARGE_FIELDS = {
    'tokenizer.ggml.tokens',
    'tokenizer.ggml.token_type',
    'tokenizer.ggml.merges',
    'tokenizer.ggml.vocab',
    'tokenizer.ggml.added_tokens',
    'tokenizer.tokens',
    'tokenizer.scores', 
    'tokenizer.merges',
    'tokenizer.ggml.special_tokens',
    'vocab',
    'special_tokens',
    'tokens',
    'merges',
    'scores'
}

# 参数映射表
PARAM_MAPPING = {
    # 注意力相关参数
    "attention.head_count": "注意力头数量",
    "head_count": "注意力头数量", 
    "attention.head_count_kv": "KV注意力头数量",
    "head_count_kv": "KV注意力头数量",
    "attention.key_length": "注意力键长度",
    "key_length": "注意力键长度",
    "attention.layer_norm_rms_epsilon": "层归一化epsilon",
    "layer_norm_rms_epsilon": "层归一化epsilon",
    "attention.value_length": "注意力值长度",
    "value_length": "注意力值长度",
    
    # 模型架构参数
    "block_count": "块数量",
    "context_length": "上下文长度",
    "embedding_length": "嵌入维度",
    "feed_forward_length": "前馈网络大小",
    "rope.dimension_count": "RoPE维度数量",
    "dimension_count": "RoPE维度数量",
    "rope.freq_base": "RoPE频率基数",
    "freq_base": "RoPE频率基数",
    "vocab_size": "词表大小",
    
    # 常规参数
    "architecture": "架构",
    "parameter_count": "参数数量",
    "file_type": "文件类型",
    "quantization_version": "量化版本",
    
    # Tokenizer相关参数
    "tokenizer.ggml.model": "分词器模型",
    "tokenizer.ggml.pre": "分词器前缀",
    "tokenizer.ggml.bos_token_id": "BOS标记ID",
    "tokenizer.ggml.eos_token_id": "EOS标记ID",
    "tokenizer.ggml.padding_token_id": "填充标记ID"
}

def calculate_vram_usage(parameter_count: float, quantization_bits: int) -> float:
    """
    计算模型的显存占用
    Args:
        parameter_count: 参数数量（以十亿为单位，例如7代表7B）
        quantization_bits: 量化位数（例如4代表4-bit量化）
    Returns:
        显存占用（GB）
    
    计算公式：VRAM = ((P * 4) / (32/Q)) * 1.2
    其中：
    - P是参数数量（单位：十亿）
    - Q是量化位数
    - 1.2是额外开销系数
    """
    try:
        # 确保输入是有效的浮点数
        P = float(parameter_count)
        Q = float(quantization_bits)
        
        # 计算显存占用：((参数量 * 4) / (32/量化位数)) * 1.2
        vram = ((P * 4) / (32/Q)) * 1.2
        return round(vram, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0

def get_quantization_bits(quantization_level: str) -> int:
    """根据量化级别获取位数"""
    return QUANTIZATION_LEVELS.get(quantization_level.upper(), {}).get('bits', 32)

def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"

def format_param_value(param_name: str, value: Any) -> str:
    """格式化参数值，根据参数类型和单位进行适当的转换"""
    try:
        if param_name not in MODEL_PARAM_SCHEMA:
            return str(value)

        param_info = MODEL_PARAM_SCHEMA[param_name]
        param_type = param_info['type']
        param_unit = param_info.get('unit')

        # 转换值到指定类型
        try:
            typed_value = param_type(value)
        except (ValueError, TypeError):
            logger.warning(f"Cannot convert {value} to type {param_type} for parameter {param_name}")
            return str(value)

        # 格式化输出
        if param_type == float:
            formatted_value = f"{typed_value:.4f}"
        else:
            formatted_value = str(typed_value)

        # 添加单位（如果有）
        if param_unit:
            formatted_value = f"{formatted_value} {param_unit}"

        return formatted_value
    except Exception as e:
        logger.error(f"Error formatting parameter value: {e}")
        return str(value)

def clean_model_name(name: str) -> str:
    """清理模型名称，移除路径和哈希值"""
    # 如果是路径，只取文件名
    name = name.replace('\\', '/').split('/')[-1]
    
    # 如果包含 sha256 哈希，移除它
    if 'sha256-' in name:
        return ''
        
    return name

def parse_parameters_string(param_str: str) -> Dict[str, Any]:
    """解析参数字符串，处理特殊格式的参数"""
    if not param_str:
        return {}
    
    params = {}
    current_key = None
    current_values = []
    
    # 按行分割参数字符串
    lines = param_str.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 使用空格分割，但保留引号内的内容
        parts = []
        current_part = []
        in_quotes = False
        for char in line:
            if char == '"':
                in_quotes = not in_quotes
                current_part.append(char)
            elif char.isspace() and not in_quotes:
                if current_part:
                    parts.append(''.join(current_part))
                    current_part = []
            else:
                current_part.append(char)
        if current_part:
            parts.append(''.join(current_part))
            
        if len(parts) >= 2:
            key = parts[0]
            value = ' '.join(parts[1:])
            
            # 处理引号
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
                
            # 尝试转换数值类型
            try:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass
                
            # 如果是相同的键，将值添加到列表中
            if key in params:
                if not isinstance(params[key], list):
                    params[key] = [params[key]]
                params[key].append(value)
            else:
                params[key] = value
                
    return params

def process_model_info(model_info: dict) -> dict:
    """
    处理模型信息，计算显存占用等
    """
    basic_info = {}
    
    # 获取基本信息
    details = model_info.get('details', {})
    parameter_size = details.get('parameter_size', '')
    
    # 处理参数规模
    if isinstance(parameter_size, str):
        try:
            parameter_count = float(parameter_size.rstrip('B'))
        except ValueError:
            parameter_count = 0
    else:
        parameter_count = float(parameter_size) if parameter_size else 0
        
    # 获取量化级别
    quantization_level = details.get('quantization_level', 'F32')
    quantization_bits = get_quantization_bits(quantization_level)
    
    # 计算显存占用
    vram_usage = calculate_vram_usage(parameter_count, quantization_bits)
    
    # 获取模型文件大小
    size_bytes = model_info.get('size', 0)
    formatted_size = format_size(size_bytes) if size_bytes else 'Unknown'
    
    # 获取最后修改时间
    modified_at = model_info.get('modified_at', '')
    if modified_at:
        try:
            # 假设时间戳是以秒为单位的
            modified_time = datetime.fromtimestamp(modified_at)
            formatted_time = modified_time.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            formatted_time = str(modified_at)
    else:
        formatted_time = 'Unknown'
    
    basic_info.update({
        'name': model_info.get('name', ''),  # 添加完整模型名称
        'base_model': details.get('base_model', ''),  # 保留基础模型名称
        'display_name': model_info.get('name', details.get('base_model', '')),  # 显示名称
        'family': details.get('family', ''),
        'families': details.get('families', []),
        'format': details.get('format', 'gguf'),
        'parameter_size': f"{parameter_size}",
        'quantization_level': quantization_level,
        'size': formatted_size,  # 使用已处理的大小
        'size_vram': f"{vram_usage:.2f} GB",
        'modified_at': formatted_time,  # 使用已处理的时间
        'digest': model_info.get('digest', '')  # 添加模型唯一标识符
    })
    
    # 添加日志记录便于调试
    logger.debug(f"Processed model info: size={formatted_size}, modified_at={formatted_time}")
    
    return basic_info

def get_category_and_key(key: str) -> tuple[str, str]:
    """获取参数类别和映射键"""
    parts = key.split('.')
    if len(parts) < 2:
        return 'general', key
        
    if parts[0] == 'general':
        return 'general', '.'.join(parts[1:])
        
    if 'tokenizer' in key.lower():
        return 'tokenizer', key
        
    if 'attention' in parts[-2:]:
        return 'attention', parts[-1]
        
    if any(term in key for term in ['block', 'embedding', 'context', 'feed', 'rope', 'vocab']):
        return 'model', parts[-1]
        
    return 'general', '.'.join(parts[1:])

def format_value(value: Any) -> str:
    """格式化参数值"""
    if isinstance(value, bool):
        return "是" if value else "否"
    elif isinstance(value, (int, float)):
        if abs(value) >= 1_000_000:
            return f"{value:,}"
        elif abs(value) < 0.0001:
            return f"{value:.2e}"
        else:
            return f"{value:g}"
    elif isinstance(value, (list, dict)):
        if len(value) > 100:
            return f"[大小: {len(value)}]"
        elif isinstance(value, list) and len(value) <= 5:
            return f"{', '.join(map(str, value))}"
        return f"[列表长度: {len(value)}]" if isinstance(value, list) else f"[字典大小: {len(value)}]"
    return str(value)

def process_advanced_info(model_specs: dict) -> dict:
    """处理高级技术参数,支持不同的模型架构"""
    advanced_info = {
        "attention": {},
        "model": {},
        "general": {},
        "tokenizer": {}
    }

    # 处理所有参数
    for full_key, value in model_specs.items():
        # 跳过大型数据字段
        if any(skip_field in full_key.lower() for skip_field in SKIP_LARGE_FIELDS):
            continue
            
        # 跳过大型数据结构
        if isinstance(value, (list, dict)) and len(str(value)) > 1000:
            continue
        
        category, key = get_category_and_key(full_key)
        display_name = PARAM_MAPPING.get(key, key.replace('_', ' ').title())
        
        formatted_value = format_value(value)
        advanced_info[category][display_name] = formatted_value

    # 修改日志记录，只记录分类和键名
    logger.debug("Processed parameters categories: %s", 
                {k: list(v.keys()) for k, v in advanced_info.items() if v})

    # 移除空类别并返回结果
    return {k: v for k, v in advanced_info.items() if v}

def process_parameters(parameters: Union[dict, str]) -> dict:
    """
    处理参数，特别是处理模板文本
    Args:
        parameters: 原始参数字典或字符串
    Returns:
        处理后的参数字典
    """
    if not parameters:
        return {}
        
    if isinstance(parameters, str):
        try:
            parameters = json.loads(parameters)
        except json.JSONDecodeError:
            logger.warning("Failed to parse parameters string")
            return {}
            
    if not isinstance(parameters, dict):
        logger.warning(f"Unexpected parameters type: {type(parameters)}")
        return {}
        
    # 处理参数
    processed = {}
    for key, value in parameters.items():
        if key == 'template':
            continue
            
        if isinstance(value, (list, dict)):
            processed[key] = f"[复杂类型，长度: {len(value)}]"
        else:
            processed[key] = format_value(value)
            
    return processed