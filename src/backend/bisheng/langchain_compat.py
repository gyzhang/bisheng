"""Langchain compatibility stubs"""
from typing import Any, Dict, List, Optional

try:
    from langchain_core.embeddings import Embeddings
    from langchain_core.messages import BaseMessage
    from langchain_core.documents import Document
    from langchain_core.language_models import BaseLanguageModel
    from langchain_core.outputs import LLMResult
    from langchain_core.agents import AgentAction, AgentFinish
    from langchain_core.runnables import Runnable
    from langchain_core.callbacks import (
        BaseCallbackHandler,
        BaseCallbackManager,
        AsyncCallbackHandler,
        CallbackManagerForChainRun,
        AsyncCallbackManagerForChainRun,
        Callbacks,
    )
except ImportError:
    pass


def create_react_agent(llm, tools, **kwargs):
    """Create a ReAct agent using langgraph.
    
    This is a compatibility function for langgraph 1.x
    """
    try:
        from langgraph.prebuilt import create_react_agent as _create_react_agent
        return _create_react_agent(llm=llm, tools=tools, **kwargs)
    except ImportError:
        from langchain.agents import create_react_agent as _create_react_agent
        return _create_react_agent(llm=llm, tools=tools, **kwargs)
