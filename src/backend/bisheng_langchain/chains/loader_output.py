"""Chain that runs an arbitrary python function."""
import functools
import logging
import json
from typing import Any, Awaitable, Callable, Dict, List, Optional

from bisheng_langchain.compat import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
    Chain,
    Document,
)

logger = logging.getLogger(__name__)


class LoaderOutputChain(Chain):
    """Chain that print the loader output.
    """
    documents: List[Document]
