from typing import Any, List

try:
    from langchain.callbacks.manager import (
        AsyncCallbackManagerForChainRun,
        CallbackManagerForChainRun,
        Callbacks,
    )
except ImportError:
    from langchain_core.callbacks import (
        AsyncCallbackManagerForChainRun,
        CallbackManagerForChainRun,
        Callbacks,
    )

try:
    from langchain.chains.base import Chain
except ImportError:
    from langchain_core.runnables import Runnable as Chain

try:
    from langchain.schema import BaseRetriever, Document
except ImportError:
    from langchain_core.retrievers import BaseRetriever
    from langchain_core.documents import Document


class RetrievalChain(Chain):
    """Chain for question-answering against a vector database."""

    retriever: BaseRetriever
    document_variable_name: str = "context"

    @property
    def input_keys(self) -> List[str]:
        return ["question"]

    @property
    def output_keys(self) -> List[str]:
        return ["answer"]

    def _call(self, inputs: dict) -> dict:
        question = inputs["question"]
        docs = self.retriever.get_relevant_documents(question)
        return {"answer": docs}

    async def _acall(self, inputs: dict) -> dict:
        question = inputs["question"]
        docs = await self.retriever.aget_relevant_documents(question)
        return {"answer": docs}
