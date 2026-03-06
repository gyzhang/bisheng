from typing import Any, Type, List, Optional

from langchain_core.documents import Document, BaseDocumentCompressor
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from bisheng.core.ai.rerank.rrf_rerank import RRFRerank

system_template = """# 任务
你是一位知识库问答助手，遵守以下规则回答问题：
1. 严谨、专业地回答用户的问题。
2. 回答时须严格基于【参考文本】中的内容：
- 如果【参考文本】中有明确与用户问题相关的文字内容，请依据相关内容进行回答；如果【参考文本】中没有任何与用户问题相关的内容，则直接回复："没有找到相关内容"。
- 如果相关内容中包含 markdown 格式的图片（例如 ![image](路径/IMAGE_1.png)），必须严格保留其原始 markdown 格式，不得添加引号、代码块（`或```）或其他特殊符号，也不得修改图片路径，保证可以正常渲染 markdown 图片。
3. 当【参考文本】中的内容来源于多个不同的信息源时，若相关内容存在明显差异或冲突，请分别列出这些差异或冲突的答案；若无差异或冲突，只给出一个统一的回答即可。

# 参考文本
{context}"""
messages = [
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template("{question}"),
]
CHAT_PROMPT = ChatPromptTemplate.from_messages(messages)


class ToolInputSchema(BaseModel):
    query: str = Field(description='question asked by the user.')


class KnowledgeRetrieverTool(BaseTool):
    name: str = "knowledge_retriever_tool"
    description: str = "在知识库中检索与查询相关的文档内容。"
    args_schema: Type[BaseModel] = ToolInputSchema

    vector_retriever: Optional[BaseRetriever] = None
    elastic_retriever: Optional[BaseRetriever] = None
    rerank: Optional[BaseDocumentCompressor] = None
    max_content: int = Field(default=15000, description='The max length of the combined document content.')
    sort_by_source_and_index: bool = Field(default=False, description='Sort by document name & chunk index.')
    rrf_weights: List[float] = Field(default=None)
    rrf_remove_zero_score: bool = Field(default=False)

    def _run(self, query: str, **kwargs: Any) -> List[Document]:
        milvus_docs, es_docs = [], []
        if self.vector_retriever:
            milvus_docs = self.vector_retriever.invoke(query)
        if self.elastic_retriever:
            es_docs = self.elastic_retriever.invoke(query)

        finally_docs = self._rrf_rerank(milvus_docs, es_docs, query)

        if self.rerank:
            finally_docs = self.rerank.compress_documents(finally_docs, query)
        return finally_docs

    async def _arun(self, query: str, **kwargs: Any) -> List[Document]:
        milvus_docs, es_docs = [], []
        if self.vector_retriever:
            milvus_docs = await self.vector_retriever.ainvoke(query)
        if self.elastic_retriever:
            es_docs = await self.elastic_retriever.ainvoke(query)

        finally_docs = self._rrf_rerank(milvus_docs, es_docs, query)

        if self.rerank:
            finally_docs = await self.rerank.acompress_documents(finally_docs, query)
        return finally_docs

    def _rrf_rerank(self, milvus_docs: List[Document], es_docs: List[Document], query: str) -> List[Document]:
        if not milvus_docs and not es_docs:
            return []
        rrf_rerank = RRFRerank(retrievers=[self.vector_retriever, self.elastic_retriever],
                               weights=self.rrf_weights,
                               remove_zero_score=self.rrf_remove_zero_score)
        finally_docs = rrf_rerank.compress_documents(documents=[es_docs, milvus_docs], query=query)

        finally_docs = self._limit_content(finally_docs)
        return finally_docs

    def _limit_content(self, docs: List[Document]) -> List[Document]:
        res_docs = []
        total_len = 0
        for doc in docs:
            doc_len = len(doc.page_content)
            if total_len + doc_len > self.max_content:
                remain = self.max_content - total_len
                if remain > 0:
                    doc.page_content = doc.page_content[:remain]
                    res_docs.append(doc)
                break
            res_docs.append(doc)
            total_len += doc_len
        return res_docs


def format_docs(docs: List[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


class KnowledgeRagTool(BaseTool):
    name: str = "knowledge_rag_tool"
    description: str = "在知识库中检索与查询相关的文档内容，并基于内容进行问答。"
    args_schema: Type[BaseModel] = ToolInputSchema

    llm: Optional[BaseChatModel] = None
    knowledge_retriever_tool: Optional[KnowledgeRetrieverTool] = None
    chat_prompt: Optional[ChatPromptTemplate] = None
    max_content: int = Field(default=15000, description='The max length of the combined document content.')
    sort_by_source_and_index: bool = Field(default=False, description='Sort by document name & chunk index.')

    @classmethod
    def from_llm(cls,
                 llm: BaseChatModel,
                 knowledge_retriever_tool: KnowledgeRetrieverTool,
                 chat_prompt: Optional[ChatPromptTemplate] = None,
                 max_content: int = 15000,
                 sort_by_source_and_index: bool = False,
                 **kwargs) -> "KnowledgeRagTool":
        if not chat_prompt:
            chat_prompt = CHAT_PROMPT
        return cls(args_schema=ToolInputSchema,
                   llm=llm,
                   chat_prompt=chat_prompt,
                   knowledge_retriever_tool=knowledge_retriever_tool,
                   max_content=max_content,
                   sort_by_source_and_index=sort_by_source_and_index,
                   **kwargs)

    def _run(self, query: str) -> Any:
        finally_docs = self.knowledge_retriever_tool.invoke({"query": query})
        qa_chain = (
            {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
            | self.chat_prompt
            | self.llm
        )
        return qa_chain.invoke({"context": format_docs(finally_docs), "question": query})

    async def _arun(self, query: str) -> Any:
        finally_docs = await self.knowledge_retriever_tool.ainvoke({"query": query})
        qa_chain = (
            {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
            | self.chat_prompt
            | self.llm
        )
        return await qa_chain.ainvoke({"context": format_docs(finally_docs), "question": query})
