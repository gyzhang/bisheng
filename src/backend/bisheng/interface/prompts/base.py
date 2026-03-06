from typing import Dict, List, Optional, Type

from bisheng.custom.customs import get_custom_nodes
from bisheng.interface.base import LangChainTypeCreator
from bisheng.interface.importing.utils import import_class
from bisheng.common.services.config_service import settings
from bisheng.template.frontend_node.prompts import PromptFrontendNode
from loguru import logger
from bisheng.utils.util import build_template_from_class

try:
    from langchain import prompts
    _HAS_LANGCHAIN_PROMPTS = True
except ImportError:
    prompts = None
    _HAS_LANGCHAIN_PROMPTS = False


class PromptCreator(LangChainTypeCreator):
    type_name: str = 'prompts'

    @property
    def frontend_node_class(self) -> Type[PromptFrontendNode]:
        return PromptFrontendNode

    @property
    def type_to_loader_dict(self) -> Dict:
        if self.type_dict is None:
            self.type_dict = {}
            if _HAS_LANGCHAIN_PROMPTS and prompts is not None:
                for prompt_name in prompts.__all__:
                    try:
                        self.type_dict[prompt_name] = import_class(f'langchain.prompts.{prompt_name}')
                    except ImportError:
                        try:
                            self.type_dict[prompt_name] = import_class(f'langchain_core.prompts.{prompt_name}')
                        except ImportError:
                            pass
            
            from bisheng.interface.prompts.custom import CUSTOM_PROMPTS

            self.type_dict.update(CUSTOM_PROMPTS)
            self.type_dict = {
                name: prompt
                for name, prompt in self.type_dict.items()
                if name in settings.prompts or settings.dev
            }
        return self.type_dict

    def get_signature(self, name: str) -> Optional[Dict]:
        try:
            if name in get_custom_nodes(self.type_name).keys():
                return get_custom_nodes(self.type_name)[name]
            return build_template_from_class(name, self.type_to_loader_dict)
        except ValueError as exc:
            logger.error(f'Prompt {name} not found: {exc}')
        except AttributeError as exc:
            logger.error(f'Prompt {name} not loaded: {exc}')
        return None

    def to_list(self) -> List[str]:
        custom_prompts = get_custom_nodes('prompts')
        return list(self.type_to_loader_dict.keys()) + list(custom_prompts.keys())


prompt_creator = PromptCreator()
