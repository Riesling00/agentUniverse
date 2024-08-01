# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/8 11:44
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: rag_chat_bot.py
from abc import abstractmethod
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse
from demo import Master
AgentUniverse().start(config_path='../../config/config.toml')


class AgentDemo():
    def __init__(self):
        self.instance: Agent = AgentManager().get_instance_obj('demo_rag_agent')
        self.instance_law: Agent = AgentManager().get_instance_obj('law_rag_agent')
        self.master = Master() 
        self.user_input = ""
        self.res_info = ""

    def chat(self):
        """ Rag agent example.

        The rag agent in agentUniverse becomes a chatbot and can ask questions to get the answer.
        """

        for i in range(5):
            # user_input = input("请输入内容,如果想退出请输入停止: ")
            if self.user_input == '停止':
                break
            print(f"\nNot only:\n")
            result = self.master.run(self.user_input)
            
            output_object: OutputObject = self.instance.run(input=self.user_input)
            output = self.instance_law.run(input=self.user_input)
            result = result + '\n' + f"\nBut also:\n"
            result += '\n' + output.get_data('output')
            result += self.output_object.get_data('output')
            
            self.res_info = result


if __name__ == '__main__':
    x = AgentDemo()
    x.chat()

