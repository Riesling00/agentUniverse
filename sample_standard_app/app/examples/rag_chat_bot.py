# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/8 11:44
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: rag_chat_bot.py
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse

AgentUniverse().start(config_path='../../config/config.toml')


def chat():
    """ Rag agent example.

    The rag agent in agentUniverse becomes a chatbot and can ask questions to get the answer.
    """
    instance: Agent = AgentManager().get_instance_obj('demo_rag_agent')
    for i in range(5):
        user_input = input("请输入内容：")
        output_object: OutputObject = instance.run(input=user_input)
        res_info = f"\nRag chat bot execution result is :\n"
        res_info += output_object.get_data('output')
        print(res_info)


if __name__ == '__main__':
    chat()

