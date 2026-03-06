"""Chain that runs an arbitrary python function."""
import functools
import inspect
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional

try:
    from langchain.chains.base import Chain
except ImportError:
    from langchain_core.runnables import Runnable as Chain

from langchain_core.callbacks import AsyncCallbackManagerForChainRun, CallbackManagerForChainRun
from pydantic import Field

logger = logging.getLogger(__name__)


class TransformChain(Chain):
    """Chain that transforms the chain output.

    Example:
        .. code-block:: python

            from bisheng_langchain.chains.transform import TransformChain
            transform_chain = TransformChain(input_variables=["text"],
             output_variables["entities"], transform=func())
    """

    input_variables: List[str]
    """The keys expected by the transform's input dictionary."""
    output_variables: List[str]
    """The keys returned by the transform's output dictionary."""
    transform_cb: Callable[[Dict[str, str]], Dict[str, str]] = Field(alias='transform')
    """The transform function."""
