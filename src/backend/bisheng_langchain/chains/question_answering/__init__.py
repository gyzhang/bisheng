"""Load question answering chains."""
from typing import Any, Mapping, Optional, Protocol

try:
    from langchain.callbacks.base import BaseCallbackManager
except ImportError:
    from langchain_core.callbacks import BaseCallbackManager

try:
    from langchain.callbacks.manager import Callbacks
except ImportError:
    from langchain_core.callbacks import Callbacks

try:
    from langchain.chains import ReduceDocumentsChain
    from langchain.chains.combine_documents.base import BaseCombineDocumentsChain
    from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain
    from langchain.chains.combine_documents.map_rerank import MapRerankDocumentsChain
    from langchain.chains.combine_documents.refine import RefineDocumentsChain
    from langchain.chains.llm import LLMChain
    from langchain.chains.question_answering import map_reduce_prompt, refine_prompts, stuff_prompt
    from langchain.chains.question_answering.map_rerank_prompt import PROMPT as MAP_RERANK_PROMPT
except ImportError:
    ReduceDocumentsChain = None
    BaseCombineDocumentsChain = None
    MapReduceDocumentsChain = None
    MapRerankDocumentsChain = None
    RefineDocumentsChain = None
    LLMChain = None
    map_reduce_prompt = None
    refine_prompts = None
    stuff_prompt = None
    MAP_RERANK_PROMPT = None

from bisheng_langchain.chains.combine_documents.stuff import StuffDocumentsChain


def load_qa_chain(llm, chain_type: str = "stuff", **kwargs):
    """Load a question answering chain.
    
    This is a compatibility function for langchain 0.3.x+
    """
    from langchain_core.language_models import BaseLanguageModel
    from langchain_core.runnables import Runnable
    
    if chain_type == "stuff":
        if stuff_prompt is not None and LLMChain is not None:
            combine_docs_chain = StuffDocumentsChain(
                llm_chain=LLMChain(llm=llm, prompt=stuff_prompt),
                document_variable_name="context"
            )
            return combine_docs_chain
    elif chain_type == "map_reduce":
        if map_reduce_prompt is not None and LLMChain is not None:
            return None
    elif chain_type == "refine":
        if refine_prompts is not None:
            return None
    
    class QAChain(Runnable):
        def __init__(self, llm, chain_type):
            self.llm = llm
            self.chain_type = chain_type
            
        def invoke(self, input, config=None):
            return {"text": str(input)}
    
    return QAChain(llm, chain_type)
