from typing import Any, ClassVar, Dict, List, Optional, Type
import inspect

from bisheng.custom.customs import get_custom_nodes
from bisheng.interface.base import LangChainTypeCreator
from bisheng.interface.importing.utils import import_class
from bisheng.common.services.config_service import settings
from bisheng.template.frontend_node.chains import ChainFrontendNode
from loguru import logger
from bisheng.utils.util import build_template_from_class, build_template_from_method
from bisheng_langchain import chains as bisheng_chains
from bisheng_langchain import sql as bisheng_sql
from bisheng_langchain.rag.bisheng_rag_chain import BishengRetrievalQA
from langchain_experimental import sql

try:
    from langchain.chains import __all__ as langchain_chains_all
except ImportError:
    langchain_chains_all = []

try:
    from langchain import chains as langchain_chains_module
except ImportError:
    langchain_chains_module = None


class ChainCreator(LangChainTypeCreator):
    type_name: str = 'chains'

    @property
    def frontend_node_class(self) -> Type[ChainFrontendNode]:
        return ChainFrontendNode

    from_method_nodes: ClassVar[Dict] = {
        'APIChain': 'from_llm_and_api_docs',
        'ConversationalRetrievalChain': 'from_llm',
        'LLMCheckerChain': 'from_llm',
        'LLMMathChain': 'from_llm',
        'QAWithSourcesChain': 'from_llm',
        'RetrievalQA': 'from_llm',
    }

    @property
    def type_to_loader_dict(self) -> Dict:
        if self.type_dict is None:
            self.type_dict: dict[str, Any] = {}
            
            if langchain_chains_module is not None:
                for chain_name in langchain_chains_all:
                    try:
                        self.type_dict[chain_name] = import_class(f'langchain.chains.{chain_name}')
                    except (ImportError, AttributeError):
                        pass
            
            bisheng = {
                chain_name: import_class(f'bisheng_langchain.chains.{chain_name}')
                for chain_name in bisheng_chains.__all__
            }
            self.type_dict['BishengRetrievalQA'] = BishengRetrievalQA
            self.type_dict.update(bisheng)

            community = {
                chain_name: import_class(f'langchain_experimental.sql.{chain_name}')
                for chain_name in sql.__all__
            }
            self.type_dict.update(community)

            bisheng_sql_add = {
                chain_name: import_class(f'bisheng_langchain.sql.{chain_name}')
                for chain_name in bisheng_sql.__all__
            }
            self.type_dict.update(bisheng_sql_add)

            from bisheng.interface.chains.custom import CUSTOM_CHAINS

            self.type_dict.update(CUSTOM_CHAINS)
            self.type_dict = {
                name: chain
                for name, chain in self.type_dict.items()
                if settings.Chains.is_not_declare(name)
            }

        return self.type_dict

    def get_available_chains(self) -> List[str]:
        return list(self.type_to_loader_dict.keys())

    def is_available_node(self, node_type: str) -> bool:
        return node_type in self.type_to_loader_dict

    def get_signature(self, name: str):
        from bisheng.template.frontend_node.base import is_subclass
        try:
            clazz = self.type_to_loader_dict[name]
            clazz = is_subclass(clazz)
            sig = inspect.signature(clazz.__init__)
            template = {}
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                field_dict = {
                    'type': str(param.annotation) if param.annotation != inspect.Parameter.empty else 'Any',
                }
                if param.default != inspect.Parameter.empty:
                    field_dict['default'] = param.default
                template[param_name] = field_dict
            return {
                'template': template,
                'base_classes': []
            }
        except Exception as e:
            logger.error(f"Error getting signature for {name}: {e}")
            return {'template': {}, 'base_classes': []}

    def to_list(self) -> List[str]:
        return list(self.type_to_loader_dict.keys())

    def get_node_class(self, node_type: str) -> Type:
        if node_type in self.from_method_nodes:
            chain_name = self.from_method_nodes[node_type]
            return build_template_from_method(
                chain_name,
                node_type,
                import_class(f'bisheng_langchain.chains.{node_type}'),
            )
        else:
            return build_template_from_class(
                node_type,
                self.type_to_loader_dict.get(node_type),
            )

    def load_flow_custom_node(self, node_data: dict, base_classes: List[Type], is_langchain: bool = False):
        from bisheng.graph.utils import strip_functions
        node_type = node_data.get('node')
        template = self.get_node_class(node_type)
        if template is None:
            raise ValueError(f'Chain {node_type} not found')
        base_classes = [strip_functions(cls) for cls in base_classes]

        return template(**node_data.get('data', {}), base_classes=base_classes)


chain_creator = ChainCreator()
