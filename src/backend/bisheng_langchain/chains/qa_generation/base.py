from __future__ import annotations

import json
import re
import logging
from typing import Any, Dict, List, Optional

try:
    from langchain_core.documents import Document
except ImportError:
    from langchain.docstore.document import Document

from langchain_core.callbacks import CallbackManagerForChainRun
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import BasePromptTemplate, ChatPromptTemplate
from pydantic import Field
from langchain_text_splitters import RecursiveCharacterTextSplitter, TextSplitter

try:
    from langchain_core.runnables import Runnable as Chain
except ImportError:
    from langchain.chains.base import Chain
    LLMChain = None

try:
    from langchain.chains.qa_generation.prompt import PROMPT_SELECTOR, CHAT_PROMPT, PROMPT
except ImportError:
    PROMPT_SELECTOR = None
    CHAT_PROMPT = None
    PROMPT = None

logger = logging.getLogger(__name__)


def parse_json(input_str: str) -> str:
    match = re.search(r'```(json)?(.*)```', input_str, re.DOTALL)
    if match is None:
        out_str = input_str
    else:
        out_str = match.group(2)
    return out_str


class QAGenerationChain(Chain):
    """Chain that generates question-answer pairs from documents."""

    llm: BaseLanguageModel
    document_variable_name: str = "text"
    input_key: str = "text"
    output_key: str = "qa"
    k: Optional[int] = None

    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    def _call(self, inputs: Dict[str, Any], run_manager: Optional[CallbackManagerForChainRun] = None) -> Dict[str, Any]:
        raise NotImplementedError("Use QAGenerationChainV2 instead")
