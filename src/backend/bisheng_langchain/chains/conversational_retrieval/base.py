from __future__ import annotations

import inspect
from typing import Any, Dict, List, Optional, Tuple, Union

from langchain_core.callbacks import AsyncCallbackManagerForChainRun, CallbackManagerForChainRun
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable

try:
    from langchain.chains.conversational_retrieval.base import \
        ConversationalRetrievalChain as BaseConversationalRetrievalChain
    _HAS_BASE_CHAIN = True
except ImportError:
    BaseConversationalRetrievalChain = None
    _HAS_BASE_CHAIN = False

# Depending on the memory type and configuration, the chat history format may differ.
# This needs to be consolidated.
CHAT_TURN_TYPE = Union[Tuple[str, str], BaseMessage]

_ROLE_MAP = {'human': 'Human: ', 'ai': 'Assistant: '}


class ConversationalRetrievalChain:
    pass
