from typing import Any, List, Tuple

from langchain_core.callbacks import Callbacks
from langchain_core.documents import Document
from langchain_core.runnables import Runnable


class StuffDocumentsChain(Runnable):
    token_max: int = -1

    def __init__(self, llm, document_variable_name: str = "context", **kwargs):
        super().__init__(**kwargs)
        self.llm = llm
        self.document_variable_name = document_variable_name

    def invoke(self, input_dict, config=None, **kwargs):
        docs = input_dict.get(self.document_variable_name, [])
        if not isinstance(docs, list):
            docs = [docs]

        text = "\n\n".join([doc.page_content if hasattr(doc, 'page_content') else str(doc) for doc in docs])

        if self.token_max > 0:
            text = text[:self.token_max]

        input_dict[self.document_variable_name] = text
        return self.llm.invoke(input_dict, config=config, **kwargs)

    async def ainvoke(self, input_dict, config=None, **kwargs):
        docs = input_dict.get(self.document_variable_name, [])
        if not isinstance(docs, list):
            docs = [docs]

        text = "\n\n".join([doc.page_content if hasattr(doc, 'page_content') else str(doc) for doc in docs])

        if self.token_max > 0:
            text = text[:self.token_max]

        input_dict[self.document_variable_name] = text
        return await self.llm.ainvoke(input_dict, config=config, **kwargs)
