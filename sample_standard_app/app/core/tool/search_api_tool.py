# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
# @Time    : 2024/6/12 09:44
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: search_api_tool.py


from typing import Optional
import threading
from langchain_community.utilities import SearchApiAPIWrapper
from pydantic import Field
from loguru import logger
import traceback
from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.util.env_util import get_from_env
os.environ['SEARCHAPI_API_KEY'] = 'ZNtsUKZ38NcxWKv9HWp2NbfZ'

_rag_query_text = """
You are a large language AI assistant built by Lepton AI. You are given a user question, and please write clean, concise and accurate answer to the question. You will be given a set of related contexts to the question, each starting with a reference number, where x is a number. Please use the context and cite the context at the end of each sentence if applicable.

Your answer must be correct, accurate and written by an expert using an unbiased and professional tone. Please limit to 1024 tokens. Do not give any information that is not related to the question, and do not repeat. Say "information is missing on" followed by the related topic, if the given context do not provide sufficient information.

Please cite the contexts with the reference numbers, in the format. If a sentence comes from multiple contexts, please list all applicable citations. Other than code and specific names and citations, your answer must be written in the same language as the question.

Remember, don't blindly repeat the contexts verbatim. And here is the user question:
"""

stop_words = [
    "<|im_end|>",
    "[End]",
    "[end]",
    "\nReferences:\n",
    "\nSources:\n",
    "End.",
]

class SearchAPITool(Tool):
    """
    The demo search tool.

    Implement the execute method of demo google search tool, using the `SearchApiAPIWrapper` to implement a simple search.

    Note:
        You need to sign up for a free account at https://www.searchapi.io/ and get the SEARCHAPI_API_KEY api key (100 free queries).

    Args:
        search_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("SEARCHAPI_API_KEY")),
        engine: str = "google" engine type you want to use
        search_params: dict = {} engine search parameters
        search_type: str = "common" result type you want to get ,common string or json
    """

    search_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("SEARCHAPI_API_KEY"))
    engine: str = "google"
    search_params: dict = {}
    search_api_wrapper: Optional[SearchApiAPIWrapper] = None
    search_type: str = "common"

    def _load_api_wapper(self):
        if not self.search_api_key:
            raise ValueError("Please set the SEARCHAPI_API_KEY environment variable.")
        if not self.search_api_wrapper:
            self.search_api_wrapper = SearchApiAPIWrapper(searchapi_api_key=self.search_api_key, engine=self.engine)
        return self.search_api_wrapper

    def execute(self, tool_input: ToolInput):
        self._load_api_wapper()
        search_params = {}
        for k, v in self.search_params.items():
            if k in tool_input.to_dict():
                search_params[k] = tool_input.get_data(k)
                continue
            search_params[k] = v
        input = tool_input.get_data("input")
        if self.search_type == "json":
            return self.search_api_wrapper.results(query=input, **search_params)
        context = self.search_api_wrapper.run(query=input, **search_params)
    

        try:
            client = self.local_client()
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": _rag_query_text},
                    {"role": "user", "content": context},
                ],
                max_tokens=1024,
                stop=stop_words,
                stream=False,
                temperature=0.9,
            )
            print("llm_response", response.choices[0].message.content)
        except Exception as e:
            logger.error(f"encountered error: {e}\n{traceback.format_exc()}")

        return response.choices[0].message.content
        

    def initialize_by_component_configer(self, component_configer: ToolConfiger) -> 'Tool':
        """Initialize the tool by the component configer."""
        super().initialize_by_component_configer(component_configer)
        self.engine = component_configer.configer.value.get('engine', 'google')
        self.search_params = component_configer.configer.value.get('search_params', {})
        self.search_type = component_configer.configer.value.get('search_type', 'common')
        return self

    def local_client(self):
        """
        Gets a thread-local client, so in case openai clients are not thread safe,
        each thread will have its own client.
        """
        import openai

        API_KEY = "sk-bcdc4facc1c14dc781a5d4885ae7ea54"
        BASE_URL = "https://api.deepseek.com"

        client = openai.OpenAI(
            base_url=BASE_URL,
            api_key=API_KEY,
            # We will set the connect timeout to be 10 seconds, and read/write
            # timeout to be 120 seconds, in case the inference server is
            # overloaded.
        )
        return client
