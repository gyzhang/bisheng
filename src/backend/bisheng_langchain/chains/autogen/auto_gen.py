"""Chain that runs an arbitrary python function."""
import functools
import json
import logging
from typing import Any, Dict, List, Optional

try:
    from autogen import ConversableAgent
    _HAS_AUTOGEN = True
except ImportError:
    ConversableAgent = None
    _HAS_AUTOGEN = False

try:
    from bisheng_langchain.autogen_role import AutoGenGroupChatManager, AutoGenUser
except ImportError:
    AutoGenGroupChatManager = None
    AutoGenUser = None

try:
    from langchain.callbacks.manager import AsyncCallbackManagerForChainRun, CallbackManagerForChainRun
except ImportError:
    from langchain_core.callbacks import AsyncCallbackManagerForChainRun, CallbackManagerForChainRun

try:
    from langchain.chains.base import Chain
except ImportError:
    from langchain_core.runnables import Runnable as Chain

logger = logging.getLogger(__name__)


class AutoGenChain(Chain):
    """Chain that print the loader output.
    """
    user_proxy_agent: AutoGenUser
    recipient: ConversableAgent
