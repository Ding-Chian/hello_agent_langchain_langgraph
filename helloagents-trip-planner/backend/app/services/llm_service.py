"""LLM服务模块"""

# from hello_agents import HelloAgentsLLM
from ..config import get_settings
from dotenv import load_dotenv
load_dotenv()
# 创建LLM实例
# llm = HelloAgentsLLM()

# # 创建LLM实例 - 框架自动检测provider
# llm = HelloAgentsLLM(moder=MODEL_ID, base_url=BASE_URL, api_key=API_KEY)

# 全局LLM实例
_llm_instance = None


# def get_llm() -> HelloAgentsLLM:
def get_llm():
    """
    获取LLM实例(单例模式)
    
    Returns:
        HelloAgentsLLM实例
    """
    global _llm_instance
    
    if _llm_instance is None:
        settings = get_settings()
        
        # HelloAgentsLLM会自动从环境变量读取配置
        # 包括OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL等
        # _llm_instance = HelloAgentsLLM()
        # 创建LLM实例 - 框架自动检测provider
        # _llm_instance = HelloAgentsLLM(moder=MODEL_ID, base_url=BASE_URL, api_key=API_KEY)
        
        # print(f"✅ LLM服务初始化成功")
        # print(f"   提供商: {_llm_instance.provider}")
        # print(f"   模型: {_llm_instance.model}")

        import os
        BASE_URL = os.getenv("BASE_URL")
        API_KEY = os.getenv("API_KEY")
        MODEL_NAME = os.getenv("MODEL_ID")
        from langchain_openai import ChatOpenAI

        _llm_instance = ChatOpenAI(
            api_key=API_KEY,
            base_url=BASE_URL,
            model=MODEL_NAME
        )
        print(f"--- 修改 ---✅ LLM服务初始化成功")
        print(f"   提供商: {BASE_URL}")
        print(f"   模型: {MODEL_NAME}")
    
    return _llm_instance


def reset_llm():
    """重置LLM实例(用于测试或重新配置)"""
    global _llm_instance
    _llm_instance = None

