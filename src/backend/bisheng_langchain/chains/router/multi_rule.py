from typing import List, Mapping

try:
    from langchain.chains.router.base import Chain, MultiRouteChain, RouterChain
except ImportError:
    from langchain_core.runnables import Runnable as Chain
    from langchain_core.runnables import Runnable as RouterChain

    class MultiRouteChain:
        pass


class MultiRuleChain(MultiRouteChain):
    router_chain: RouterChain
    destination_chains: Mapping[str, Chain]
    default_chain: Chain
    output_variables: List[str]

    @property
    def output_keys(self) -> List[str]:
        return self.output_variables
