try:
    from langchain_core.runs import CommonLLMParams
except ImportError:
    CommonLLMParams = None

try:
    from langchain_core.language_models import BaseLanguageModel
except ImportError:
    BaseLanguageModel = None

try:
    from langchain_core.embeddings import Embeddings
except ImportError:
    Embeddings = None

try:
    from langchain_core.documents import Document
except ImportError:
    Document = None

try:
    from langchain_core.memory import BaseMemory
except ImportError:
    BaseMemory = None

from langchain_anthropic import ChatAnthropic
from langchain_community import agent_toolkits, document_loaders
from langchain_community import embeddings as lc_embeddings
from langchain_community.chat_models import ChatVertexAI, MiniMaxChat, ChatTongyi, ChatZhipuAI
from langchain_community.utilities import requests
from langchain_deepseek import ChatDeepSeek
from langchain_openai import AzureChatOpenAI, ChatOpenAI, OpenAIEmbeddings, AzureOpenAIEmbeddings, OpenAI

CUSTOM_NODES = {
    'ChatAnthropic': ChatAnthropic,
    'ChatVertexAI': ChatVertexAI,
    'MiniMaxChat': MiniMaxChat,
    'ChatTongyi': ChatTongyi,
    'ChatZhipuAI': ChatZhipuAI,
    'ChatDeepSeek': ChatDeepSeek,
    'AzureChatOpenAI': AzureChatOpenAI,
    'ChatOpenAI': ChatOpenAI,
    'OpenAIEmbeddings': OpenAIEmbeddings,
    'AzureOpenAIEmbeddings': AzureOpenAIEmbeddings,
    'OpenAI': OpenAI,
}

documentloaders_type_to_cls_dict = {}
embedding_type_to_cls_dict = {}
llm_type_to_cls_dict = {}
memory_type_to_cls_dict = {}
textsplitter_type_to_cls_dict = {}
