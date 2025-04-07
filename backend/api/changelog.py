from fastapi import APIRouter, HTTPException
import os
import logging
from data_path import get_changelog_path

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/changelog")
async def get_changelog():
    try:
        # 使用数据路径管理模块获取CHANGELOG.md文件路径
        changelog_path = get_changelog_path()
        
        logger.info(f"尝试获取更新日志，路径: {changelog_path}")
        
        if changelog_path and os.path.exists(changelog_path):
            # 读取更新日志文件
            logger.info(f"找到更新日志文件，正在读取: {changelog_path}")
            with open(changelog_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            logger.info(f"成功读取更新日志，大小: {len(content)} 字节")
            return {"content": content}
        else:
            # 如果找不到文件，返回默认内容
            logger.warning(f"未找到更新日志文件: {changelog_path}")
            fallback_content = """# 更新日志

## [0.0.1] - 2025-04-07

### 新增
- windows客户端，开箱即用！

### 优化
- 无

### 修复
- 无"""
            logger.info("返回默认更新日志内容")
            return {"content": fallback_content}
    except Exception as e:
        logger.error(f"读取更新日志失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to read changelog file: {str(e)}")