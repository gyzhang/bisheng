from typing import ClassVar, Dict, List, Optional, Type

from bisheng.interface.base import LangChainTypeCreator
from bisheng.interface.importing.utils import import_class
from bisheng.common.services.config_service import settings
from bisheng.template.frontend_node.output_parsers import OutputParserFrontendNode
from loguru import logger
from bisheng.utils.util import build_template_from_class, build_template_from_method

try:
    from langchain import output_parsers
    _HAS_LANGCHAIN = True
except ImportError:
    output_parsers = None
    _HAS_LANGCHAIN = False


class OutputParserCreator(LangChainTypeCreator):
    type_name: str = 'output_parsers'
    from_method_nodes: ClassVar[Dict] = {
        'StructuredOutputParser': 'from_response_schemas',
    }

    @property
    def frontend_node_class(self) -> Type[OutputParserFrontendNode]:
        return OutputParserFrontendNode

    @property
    def type_to_loader_dict(self) -> Dict:
        if self.type_dict is None:
            self.type_dict = {}
            if _HAS_LANGCHAIN and output_parsers is not None:
                for output_parser_name in output_parsers.__all__:
                    if not settings.dev and output_parser_name not in settings.output_parsers:
                        continue
                    if output_parser_name == "GuardrailsOutputParser":
                        self.type_dict[output_parser_name] = import_class(f'langchain_community.output_parsers.rail_parser.{output_parser_name}')
                    else:
                        try:
                            self.type_dict[output_parser_name] = import_class(f'langchain.output_parsers.{output_parser_name}')
                        except ImportError:
                            try:
                                self.type_dict[output_parser_name] = import_class(f'langchain_core.output_parsers.{output_parser_name}')
                            except ImportError:
                                pass
        return self.type_dict

    def get_signature(self, name: str) -> Optional[Dict]:
        try:
            if name in self.from_method_nodes:
                return build_template_from_method(
                    name,
                    type_to_cls_dict=self.type_to_loader_dict,
                    method_name=self.from_method_nodes[name],
                )
            else:
                return build_template_from_class(name, self.type_to_loader_dict.get(name))
        except Exception as e:
            logger.error(f"Error getting signature for {name}: {e}")
            return {}

    def to_list(self) -> List[str]:
        return list(self.type_to_loader_dict.keys())


output_parser_creator = OutputParserCreator()
