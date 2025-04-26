import json
import logging
import re
from typing import Dict, Any, List, AsyncGenerator

from ollama.types import ChatRequest, ChatMessage

from api.tools.doc_format import get_mime_type_from_filename
from .client_pool import get_available_client

async def process_chat_messages(
    messages: List[Dict[str, Any]],
    model: str,
    web_search: bool = False,
    username: str = None,
    client=None,
    client_index=None,
    semaphore=None
) -> AsyncGenerator[str, None]:
    """处理聊天消息并生成响应流
    
    Args:
        messages: 聊天消息列表
        model: 模型名称
        web_search: 是否启用网页搜索
        username: 用户名
        client: 预先获取的客户端对象，如果提供则使用此客户端
        client_index: 客户端索引
        semaphore: 客户端信号量
    """
    # 如果未提供客户端，则获取可用的客户端实例
    if client is None or semaphore is None:
        client, client_index, semaphore = await get_available_client(model=model)
    
    # 使用信号量控制对客户端的访问
    async with semaphore:
        try:
            logging.info(f"开始处理聊天消息，使用模型: {model}, 网页搜索: {web_search}, 客户端索引: {client_index}")
            # 转换消息格式，确保图片数据正确传递
            formatted_messages = []
            for msg in messages:
                formatted_msg = {
                    "role": msg["role"],
                    "content": msg["content"]
                }
                # 如果有图片数据，添加到消息中
                if "image" in msg and msg["image"]:
                    formatted_msg["images"] = [msg["image"]]  # Ollama API 需要 images 数组
                
                # 如果有文档数据，将文档内容添加到消息中
                if "document" in msg and msg["document"]:
                    # 获取文档内容
                    doc_content = msg["document"]
                    file_name = "文档"
                    
                    # 处理文档内容，确保它是字符串类型
                    if isinstance(doc_content, dict):
                        # 如果是字典格式，提取内容和文件名
                        if "content" in doc_content:
                            file_name = doc_content.get("name", "文档")
                            doc_content = doc_content["content"]
                        else:
                            # 如果没有content字段，转换整个字典为字符串
                            doc_content = json.dumps(doc_content, ensure_ascii=False)
                    elif not isinstance(doc_content, str):
                        # 如果不是字符串也不是字典，尝试转换为字符串
                        try:
                            doc_content = str(doc_content)
                        except Exception as e:
                            logging.error(f"文档内容转换失败: {str(e)}")
                            doc_content = "无法读取文档内容"
                    
                    # 现在doc_content应该是字符串类型，可以安全使用正则表达式
                    # 尝试从内容中提取文件名（如果尚未从字典中获取）
                    if isinstance(doc_content, str) and file_name == "文档":
                        match = re.search(r"# 文件: (.+?)\n", doc_content)
                        if match:
                            file_name = match.group(1)
                    
                    # 如果文档内容太长，可能需要截断
                    if isinstance(doc_content, str):
                        max_doc_length = 200000  # 设置一个合理的最大长度
                        if len(doc_content) > max_doc_length:
                            doc_content = doc_content[:max_doc_length] + "...\n[文档内容过长，已截断]"
                    
                    # 添加文档内容到消息中
                    formatted_msg["content"] = formatted_msg["content"] + f"\n\n以下是《{file_name}》的内容：\n" + doc_content
                    
                    # 打印调试信息
                    logging.debug(f"添加文档内容到消息中，文档名称: {file_name}，文档长度: {len(str(doc_content))}")
                
                formatted_messages.append(formatted_msg)

            # 如果启用了网页搜索，调用 Tavily 搜索工具
            if web_search and messages[-1]["role"] == "user":
                from api.tools.tavily_search import search_web
                try:
                    search_query = messages[-1]["content"]
                    search_results = await search_web(search_query, username=username)
                    
                    # 检查搜索结果
                    if search_results and "results" in search_results and search_results["results"]:
                        # 将搜索结果添加到系统消息中
                        search_content = "\n\n网页搜索结果:\n"
                        for idx, result in enumerate(search_results["results"], 1):
                            search_content += f"{idx}. {result['title']}: {result['url']}\n{result['content']}\n\n"
                        
                        # 添加系统消息，提供搜索结果
                        formatted_messages.insert(0, {
                            "role": "system",
                            "content": "你必须使用以下网页搜索结果来回答用户的问题。如果搜索结果中包含答案，请基于这些结果回答，而不是使用你自己的知识。以下是搜索结果：" + search_content
                        })
                        logging.info(f"已添加网页搜索结果到消息中")
                    elif search_results and "error" in search_results:
                        # 如果有错误，添加错误信息到系统消息
                        error_message = search_results["error"]
                        formatted_messages.insert(0, {
                            "role": "system",
                            "content": f"用户启用了网页搜索功能，但搜索失败: {error_message}。请在回答中告知用户搜索功能当前不可用，建议检查Tavily API密钥配置。"
                        })
                        logging.warning(f"网页搜索失败: {error_message}")
                    else:
                        # 如果没有结果，添加提示信息
                        formatted_messages.insert(0, {
                            "role": "system",
                            "content": "用户启用了网页搜索功能，但未找到相关搜索结果。请基于您已有的知识回答问题。"
                        })
                        logging.info("网页搜索未返回结果")
                except Exception as e:
                    # 捕获搜索过程中的异常
                    error_message = str(e)
                    formatted_messages.insert(0, {
                        "role": "system",
                        "content": f"用户启用了网页搜索功能，但搜索过程中发生错误: {error_message}。请在回答中告知用户搜索功能当前不可用。"
                    })
                    logging.error(f"网页搜索异常: {error_message}")
                    
            # 在用户最后一条消息后添加搜索结果（仅当启用网页搜索且有搜索结果时）
            if web_search and 'search_content' in locals() and search_results and "results" in search_results and search_results["results"]:
                for i in range(len(formatted_messages) - 1, -1, -1):
                    if formatted_messages[i]["role"] == "user":
                        formatted_messages.insert(i + 1, {
                            "role": "system",
                            "content": f"以下是与用户问题相关的网页搜索结果：{search_content}"
                        })
                        break

            chat_request = ChatRequest(
                model=model,
                messages=[ChatMessage(**msg) for msg in formatted_messages],
                stream=True
            )
            
            try:
                # 使用分配的客户端处理请求
                async for chunk in client.chat(chat_request):
                    yield json.dumps({
                        "model": model,
                        "message": {
                            "role": "assistant",
                            "content": chunk.message.content if chunk.message else ""
                        },
                        "done": chunk.done
                    })
            except AttributeError as e:
                # 特别处理可能的元组或对象属性错误
                error_msg = f"客户端对象类型错误: {type(client)}, 错误: {str(e)}"
                logging.error(error_msg)
                logging.exception(e)
                yield json.dumps({
                    "error": error_msg,
                    "model": model,
                    "message": {
                        "role": "assistant",
                        "content": f"抱歉，与AI模型通信时出现错误：{str(e)}"
                    }
                })
                
            logging.info(f"完成处理聊天消息，客户端索引: {client_index}")
        except Exception as e:
            error_msg = f"处理消息时出错: {str(e)}"
            logging.error(f"客户端 {client_index} 处理消息时出错: {error_msg}")
            logging.exception(e)  # 记录完整的错误堆栈
            yield json.dumps({
                "error": error_msg,
                "model": model,
                "message": {
                    "role": "assistant",
                    "content": f"抱歉，处理消息时出现错误：{str(e)}"
                }
            })

def get_limited_history(messages, max_messages=20):
    """限制历史消息数量，保留最近的消息"""
    if len(messages) <= max_messages:
        return messages
    
    # 保留最后 max_messages 条消息
    limited_messages = messages[-max_messages:]
    
    # 确保每条消息都有正确的格式
    for msg in limited_messages:
        # 确保文档字段格式正确
        if "document" in msg and msg["document"]:
            # 获取文档内容
            document_content = msg["document"]
            file_name = "document.md"
            file_type = get_mime_type_from_filename(file_name)
            
            # 如果文档内容是字典，提取其中的内容
            if isinstance(document_content, dict):
                if "name" in document_content:
                    file_name = document_content["name"]
                    file_type = get_mime_type_from_filename(file_name)
                
                if "content" in document_content:
                    document_content = document_content["content"]
                else:
                    # 如果没有content字段，则将整个字典转换为字符串
                    document_content = json.dumps(document_content, ensure_ascii=False)
            elif not isinstance(document_content, str):
                # 如果不是字符串也不是字典，尝试转换为字符串
                try:
                    document_content = str(document_content)
                except:
                    document_content = "无法读取文档内容"
            
            # 现在document_content应该是字符串，可以安全使用正则表达式
            # 从Markdown内容中提取文件名（如果尚未从字典中获取）
            if isinstance(document_content, str) and file_name == "document.md":
                match = re.search(r"# 文件: (.+?)\n", document_content)
                if match:
                    file_name = match.group(1)
                    file_type = get_mime_type_from_filename(file_name)
            
            # 构建文档对象，用于前端显示
            msg["document"] = {
                "name": file_name,
                "content": document_content,
                "type": file_type
            }
    
    return limited_messages 