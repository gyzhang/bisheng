"""
Compatibility module for langchain imports.
This module provides fallback imports for langchain APIs that have been
moved or removed in langchain 0.3.x+
"""

try:
    from langchain.callbacks.manager import (
        AsyncCallbackManagerForChainRun,
        CallbackManagerForChainRun,
        Callbacks,
        BaseCallbackManager,
    )
except ImportError:
    from langchain_core.callbacks import (
        AsyncCallbackManagerForChainRun,
        CallbackManagerForChainRun,
        Callbacks,
    )
    BaseCallbackManager = object

try:
    from langchain.chains.base import Chain
except ImportError:
    from langchain_core.runnables import Runnable as Chain

try:
    from langchain.docstore.document import Document
except ImportError:
    from langchain_core.documents import Document

try:
    from langchain.schema import BaseRetriever
except ImportError:
    from langchain_core.retrievers import BaseRetriever

try:
    from langchain.chains.combine_documents.stuff import StuffDocumentsChain as BaseStuffDocumentsChain
except ImportError:
    BaseStuffDocumentsChain = None

try:
    from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain as BaseConversationalRetrievalChain
except ImportError:
    BaseConversationalRetrievalChain = None

try:
    from langchain.chains.question_answering import load_qa_chain
except ImportError:
    load_qa_chain = None
