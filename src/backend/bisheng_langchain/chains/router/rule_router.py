import asyncio
from typing import Any, Callable, Dict, List, Union

try:
    from langchain.callbacks.manager import Callbacks
except ImportError:
    from langchain_core.callbacks import Callbacks

try:
    from langchain.chains.router.base import Route, RouterChain
except ImportError:
    from langchain_core.runnables import Runnable as RouterChain

    class Route:
        pass


class RuleBasedRouter(RouterChain):
    rule_function: Callable[..., str]
    input_variables: List[str]

    @property
    def input_keys(self):
        return self.input_variables
