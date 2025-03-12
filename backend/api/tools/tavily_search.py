"""
Tavily搜索工具 - 为Ollama LLM提供网页搜索功能
"""
import os
import logging
from typing import Dict, Any, Optional, List
from tavily import TavilyClient
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from api.auth import get_current_user
from config import API_CONFIG
from database import Database, get_db

router = APIRouter()

# 全局变量
TAVILY_API_KEY = API_CONFIG.get("TAVILY_API_KEY", "")

# 创建Tavily客户端
tavily_client = None
if TAVILY_API_KEY:
    try:
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
        logging.info("Tavily客户端初始化成功")
    except Exception as e:
        logging.error(f"Tavily客户端初始化失败: {str(e)}")

# 定义请求模型
class TavilySettings(BaseModel):
    api_key: Optional[str] = None
    search_depth: Optional[str] = "basic"  # 默认为基础搜索
    include_domains: Optional[List[str]] = None  # 包含的域名列表
    exclude_domains: Optional[List[str]] = None  # 排除的域名列表

class SearchRequest:
    def __init__(self, query: str, search_depth: str = "basic", max_results: int = 5):
        self.query = query
        self.search_depth = search_depth
        self.max_results = max_results

# 获取Tavily API设置
@router.get("/settings")
async def get_tavily_settings(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    获取Tavily API设置
    """
    try:
        # 从数据库获取设置
        settings = {}
        
        # 获取API密钥
        api_key_setting = await db.fetch_one(
            """
            SELECT value FROM settings
            WHERE key = 'tavily_api_key' AND user_id = ?
            """,
            (current_user["username"],)
        )
        
        if api_key_setting:
            # 返回设置，但隐藏完整的API密钥
            api_key = api_key_setting["value"]
            masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "****"
            settings["api_key"] = masked_key
        else:
            settings["api_key"] = ""
            
        # 获取搜索深度设置
        search_depth_setting = await db.fetch_one(
            """
            SELECT value FROM settings
            WHERE key = 'tavily_search_depth' AND user_id = ?
            """,
            (current_user["username"],)
        )
        settings["search_depth"] = search_depth_setting["value"] if search_depth_setting else "basic"
        
        # 获取包含域名设置
        include_domains_setting = await db.fetch_one(
            """
            SELECT value FROM settings
            WHERE key = 'tavily_include_domains' AND user_id = ?
            """,
            (current_user["username"],)
        )
        include_domains_value = include_domains_setting["value"] if include_domains_setting else ""
        settings["include_domains"] = include_domains_value.split(",") if include_domains_value else []
        
        # 获取排除域名设置
        exclude_domains_setting = await db.fetch_one(
            """
            SELECT value FROM settings
            WHERE key = 'tavily_exclude_domains' AND user_id = ?
            """,
            (current_user["username"],)
        )
        exclude_domains_value = exclude_domains_setting["value"] if exclude_domains_setting else ""
        settings["exclude_domains"] = exclude_domains_value.split(",") if exclude_domains_value else []
        
        return settings
    except Exception as e:
        logging.error(f"获取Tavily API设置失败: {str(e)}")
        # 返回默认设置而不是抛出异常
        return {
            "api_key": "",
            "search_depth": "basic",
            "include_domains": [],
            "exclude_domains": []
        }

# 更新Tavily API设置
@router.post("/settings")
async def update_tavily_settings(
    settings: TavilySettings,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    更新Tavily API设置
    """
    try:
        # 如果提供了API密钥，则检查其有效性
        if settings.api_key and settings.api_key.strip():
            try:
                test_client = TavilyClient(api_key=settings.api_key)
                # 执行一个简单的测试查询
                test_client.search("test", max_results=1)
                
                # 更新数据库中的API密钥设置
                await db.execute(
                    """
                    INSERT OR REPLACE INTO settings (key, value, user_id, created_at, updated_at)
                    VALUES (?, ?, ?, datetime('now'), datetime('now'))
                    """,
                    ("tavily_api_key", settings.api_key, current_user["username"])
                )
                
                # 更新全局变量
                global TAVILY_API_KEY, tavily_client
                TAVILY_API_KEY = settings.api_key
                tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"API密钥无效: {str(e)}"
                )
        
        # 更新搜索深度设置
        if settings.search_depth is not None:
            await db.execute(
                """
                INSERT OR REPLACE INTO settings (key, value, user_id, created_at, updated_at)
                VALUES (?, ?, ?, datetime('now'), datetime('now'))
                """,
                ("tavily_search_depth", settings.search_depth, current_user["username"])
            )
        
        # 更新包含域名设置
        if settings.include_domains is not None:
            await db.execute(
                """
                INSERT OR REPLACE INTO settings (key, value, user_id, created_at, updated_at)
                VALUES (?, ?, ?, datetime('now'), datetime('now'))
                """,
                ("tavily_include_domains", ",".join(settings.include_domains) if settings.include_domains else "", current_user["username"])
            )
        
        # 更新排除域名设置
        if settings.exclude_domains is not None:
            await db.execute(
                """
                INSERT OR REPLACE INTO settings (key, value, user_id, created_at, updated_at)
                VALUES (?, ?, ?, datetime('now'), datetime('now'))
                """,
                ("tavily_exclude_domains", ",".join(settings.exclude_domains) if settings.exclude_domains else "", current_user["username"])
            )
        
        return {"status": "success", "message": "Tavily API设置已更新"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"更新Tavily API设置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新设置失败: {str(e)}"
        )

# 测试Tavily API连接
@router.post("/test")
async def test_tavily_connection(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    测试Tavily API连接
    """
    try:
        # 从数据库获取API密钥
        setting = await db.fetch_one(
            """
            SELECT value FROM settings
            WHERE key = 'tavily_api_key' AND user_id = ?
            """,
            (current_user["username"],)
        )
        
        if not setting or not setting["value"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未设置Tavily API密钥"
            )
        
        # 测试连接
        try:
            test_client = TavilyClient(api_key=setting["value"])
            response = test_client.search("test connection", max_results=1)
            return {"status": "success", "message": "Tavily API连接成功", "response": response}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"API连接失败: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"测试Tavily API连接失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"测试连接失败: {str(e)}"
        )

# 检查用户是否设置了Tavily API密钥
@router.get("/check-api-key")
async def check_tavily_api_key(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """
    检查用户是否设置了Tavily API密钥
    """
    try:
        # 从数据库获取API密钥
        api_key_setting = await db.fetch_one(
            """
            SELECT value FROM settings
            WHERE key = 'tavily_api_key' AND user_id = ?
            """,
            (current_user["username"],)
        )
        
        # 全局API密钥检查
        has_global_api_key = bool(TAVILY_API_KEY)
        
        # 用户API密钥检查
        has_user_api_key = bool(api_key_setting and api_key_setting["value"])
        
        return {
            "has_api_key": has_global_api_key or has_user_api_key
        }
    except Exception as e:
        logging.error(f"检查Tavily API密钥失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检查API密钥失败: {str(e)}"
        )

@router.post("/search")
async def search(
    query: str,
    search_depth: str = "basic",
    max_results: int = 5,
    include_answer: bool = True,
    include_domains: Optional[str] = None,
    exclude_domains: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    执行Tavily搜索
    
    Args:
        query: 搜索查询
        search_depth: 搜索深度，可选值为"basic"或"advanced"
        max_results: 返回结果数量
        include_answer: 是否包含AI生成的答案
        include_domains: 包含的域名，多个域名用逗号分隔
        exclude_domains: 排除的域名，多个域名用逗号分隔
        
    Returns:
        搜索结果
    """
    if not tavily_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Tavily搜索服务未配置，请设置TAVILY_API_KEY环境变量"
        )
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="搜索查询不能为空"
        )
    
    try:
        # 执行搜索
        response = tavily_client.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results,
            include_answer="basic" if include_answer else False,
            include_domains=include_domains,
            exclude_domains=exclude_domains
        )
        
        return response
    except Exception as e:
        logging.error(f"Tavily搜索失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索失败: {str(e)}"
        )

@router.post("/search_context")
async def search_context(
    query: str,
    search_depth: str = "basic",
    include_domains: Optional[str] = None,
    exclude_domains: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取搜索上下文，适用于RAG应用
    
    Args:
        query: 搜索查询
        search_depth: 搜索深度，可选值为"basic"或"advanced"
        include_domains: 包含的域名，多个域名用逗号分隔
        exclude_domains: 排除的域名，多个域名用逗号分隔
        
    Returns:
        搜索上下文
    """
    if not tavily_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Tavily搜索服务未配置，请设置TAVILY_API_KEY环境变量"
        )
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="搜索查询不能为空"
        )
    
    try:
        # 获取搜索上下文
        context = tavily_client.get_search_context(
            query=query,
            search_depth=search_depth,
            include_domains=include_domains,
            exclude_domains=exclude_domains
        )
        
        return {"context": context}
    except Exception as e:
        logging.error(f"获取Tavily搜索上下文失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取搜索上下文失败: {str(e)}"
        )

@router.post("/qna")
async def qna_search(
    query: str,
    search_depth: str = "basic",
    include_domains: Optional[str] = None,
    exclude_domains: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    问答搜索，直接返回问题的答案
    
    Args:
        query: 问题
        search_depth: 搜索深度，可选值为"basic"或"advanced"
        include_domains: 包含的域名，多个域名用逗号分隔
        exclude_domains: 排除的域名，多个域名用逗号分隔
        
    Returns:
        问题的答案
    """
    if not tavily_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Tavily搜索服务未配置，请设置TAVILY_API_KEY环境变量"
        )
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="问题不能为空"
        )
    
    try:
        # 执行问答搜索
        response = tavily_client.qna_search(
            query=query,
            search_depth=search_depth,
            include_domains=include_domains,
            exclude_domains=exclude_domains
        )
        
        return response
    except Exception as e:
        logging.error(f"Tavily问答搜索失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"问答搜索失败: {str(e)}"
        )

# 为消息处理提供的网页搜索函数
async def search_web(query: str, search_depth: str = None, max_results: int = 5, include_domains: Optional[str] = None, exclude_domains: Optional[str] = None, username: str = None) -> Dict[str, Any]:
    """
    执行网页搜索，供消息处理使用
    
    Args:
        query: 搜索查询
        search_depth: 搜索深度，可选值为"basic"或"advanced"，如果为None则使用用户设置
        max_results: 返回结果数量
        include_domains: 包含的域名，多个域名用逗号分隔，如果为None则使用用户设置
        exclude_domains: 排除的域名，多个域名用逗号分隔，如果为None则使用用户设置
        username: 用户名，用于获取用户设置
        
    Returns:
        搜索结果
    """
    global tavily_client, TAVILY_API_KEY
    user_api_key = None
    
    # 如果未提供搜索深度或域名过滤，且提供了用户名，则尝试从数据库获取用户设置
    if username:
        try:
            # 获取数据库连接
            db = await get_db().__anext__()
            
            # 获取API密钥
            api_key_setting = await db.fetch_one(
                """
                SELECT value FROM settings
                WHERE key = 'tavily_api_key' AND user_id = ?
                """,
                (username,)
            )
            
            if api_key_setting and api_key_setting["value"]:
                user_api_key = api_key_setting["value"]
                logging.info(f"从数据库获取到用户 {username} 的API密钥")
            
            # 如果未提供搜索深度，则获取用户设置的搜索深度
            if search_depth is None:
                search_depth_setting = await db.fetch_one(
                    """
                    SELECT value FROM settings
                    WHERE key = 'tavily_search_depth' AND user_id = ?
                    """,
                    (username,)
                )
                search_depth = search_depth_setting["value"] if search_depth_setting else "basic"
            
            # 如果未提供包含域名，则获取用户设置的包含域名
            if include_domains is None:
                include_domains_setting = await db.fetch_one(
                    """
                    SELECT value FROM settings
                    WHERE key = 'tavily_include_domains' AND user_id = ?
                    """,
                    (username,)
                )
                include_domains = include_domains_setting["value"].split(",") if include_domains_setting and include_domains_setting["value"] else None
            
            # 如果未提供排除域名，则获取用户设置的排除域名
            if exclude_domains is None:
                exclude_domains_setting = await db.fetch_one(
                    """
                    SELECT value FROM settings
                    WHERE key = 'tavily_exclude_domains' AND user_id = ?
                    """,
                    (username,)
                )
                exclude_domains = exclude_domains_setting["value"].split(",") if exclude_domains_setting and exclude_domains_setting["value"] else None
        except Exception as e:
            logging.error(f"获取用户Tavily设置失败: {str(e)}")
            # 使用默认值
            if search_depth is None:
                search_depth = "basic"
    elif search_depth is None:
        # 如果未提供搜索深度且没有用户名，则使用默认值
        search_depth = "basic"
    
    # 尝试使用用户的API密钥
    if user_api_key:
        try:
            logging.info(f"尝试使用用户 {username} 的API密钥进行搜索")
            temp_client = TavilyClient(api_key=user_api_key)
            response = temp_client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_domains=include_domains,
                exclude_domains=exclude_domains
            )
            
            # 如果成功，更新全局客户端
            TAVILY_API_KEY = user_api_key
            tavily_client = temp_client
            logging.info(f"使用用户 {username} 的API密钥搜索成功")
            
            return response
        except Exception as e:
            logging.error(f"使用用户 {username} 的API密钥搜索失败: {str(e)}")
    
    # 尝试使用全局客户端
    if tavily_client:
        try:
            logging.info("尝试使用全局客户端进行搜索")
            # 执行搜索
            response = tavily_client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_domains=include_domains,
                exclude_domains=exclude_domains
            )
            logging.info("使用全局客户端搜索成功")
            return response
        except Exception as e:
            logging.error(f"使用全局客户端搜索失败: {str(e)}")
    
    # 如果全局客户端不可用或搜索失败，尝试使用环境变量中的API密钥
    if API_CONFIG.get("TAVILY_API_KEY"):
        try:
            logging.info("尝试使用环境变量中的API密钥进行搜索")
            temp_client = TavilyClient(api_key=API_CONFIG["TAVILY_API_KEY"])
            response = temp_client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_domains=include_domains,
                exclude_domains=exclude_domains
            )
            logging.info("使用环境变量中的API密钥搜索成功")
            return response
        except Exception as e:
            logging.error(f"使用环境变量API密钥搜索失败: {str(e)}")
    
    # 如果所有尝试都失败
    logging.warning("所有搜索尝试都失败，未配置有效的Tavily API密钥")
    return {"error": "无法执行搜索，未配置有效的Tavily API密钥"}
