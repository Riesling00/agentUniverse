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

from openai import OpenAI
AgentUniverse().start(config_path='../../config/config.toml')
API_KEY = "sk-bcdc4facc1c14dc781a5d4885ae7ea54"
BASE_URL = "https://api.deepseek.com"
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

class AgentDemo():
    def __init__(self):
        self.instance: Agent = AgentManager().get_instance_obj('demo_rag_agent')
        self.instance_law: Agent = AgentManager().get_instance_obj('law_rag_agent')
        self.master = Master() 
        self.user_input = ""
        self.res_info = ""

    def chat(self, user_input = None):
        """ Rag agent example.

        The rag agent in agentUniverse becomes a chatbot and can ask questions to get the answer.
        """
        self.user_input = user_input
        if self.user_input == '停止':
            exit
        print(f"\nNot only:\n")
        result = f"\nNot only:\n" + self.master.run(self.user_input)["output"]
            
        output_object: OutputObject = self.instance.run(input=self.user_input)
        output = self.instance_law.run(input=self.user_input)
        result += '\n' + f"\nBut also:\n"
        result += '\n' + output.get_data('output')
        result += '\n' + output_object.get_data('output')
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant，把输入内容进行，保持感情基调"},
                {"role": "user", "content": result},
            ],
            stream=False
        ).choices[0].message.content
        self.res_info = response
        print(f"\n{response}")
        return response

if __name__ == '__main__':
    x = AgentDemo()
    for i in range(5):
        user_input = input("请输入内容,如果想退出请输入停止: ")
        x.chat(user_input)

