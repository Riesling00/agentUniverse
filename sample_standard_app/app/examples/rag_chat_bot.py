# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import copy
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

import time

import multiprocessing


class Timer():
    def __init__(self):
        self.st_time = self.ed_time = time.time()
    
    def start(self):
        self.st_time = time.time()
    
    def stop(self,msg):
        self.ed_time = time.time()
        time_gap = self.ed_time-self.st_time
        print(f"[Test info]: {msg}: {time_gap:.2f} sec")
        return time_gap


master = Master()
def master_run(user_input,results_q):
    timer = Timer()
    timer.start()
    output = master.run(user_input)
    time_cost = timer.stop("master_run")
    results_q.put(["master",output,time_cost])


instance = AgentManager().get_instance_obj('demo_rag_agent')
def instance_run(user_input,results_q):
    timer = Timer()
    timer.start()
    output = instance.run(input=user_input)
    time_cost = timer.stop("instance_run")
    results_q.put(["instance",output,time_cost])

instance_law = AgentManager().get_instance_obj('law_rag_agent')
def instance_law_run(user_input,results_q):
    timer = Timer()
    timer.start()
    output = instance_law.run(input=user_input)
    time_cost = timer.stop("instance_law_run")
    results_q.put(["instance_law",output,time_cost])
    

class AgentDemo():
    def __init__(self):
        self.instance: Agent = AgentManager().get_instance_obj('demo_rag_agent')
        self.instance_law: Agent = AgentManager().get_instance_obj('law_rag_agent')
        self.master = Master()
        self.user_input = ""
        self.res_info = ""

    def instance_run(self,input):
        return self.instance.run(input=input)

    def chat(self, user_input = None):
        """ Rag agent example.

        The rag agent in agentUniverse becomes a chatbot and can ask questions to get the answer.
        """
        if user_input != None:
            self.user_input = user_input
        if self.user_input == '停止':
            exit
        print(f"\nNot only:\n")

        # An instance in the results_q should be [ results_type , results , time_cost]
        # results_type shoule be one string of ['master', 'instance', 'instance_law','chat.completions']
        results_q = multiprocessing.Queue()
        process_master = multiprocessing.Process(target=master_run,args=(self.user_input,results_q) )
        process_instance = multiprocessing.Process(target=instance_run,args=(self.user_input,results_q) )
        process_instance_law = multiprocessing.Process(target=instance_law_run,args=(self.user_input,results_q) )
        process_list = [process_master, process_instance, process_instance_law]
        
        chat_timer = Timer()
        chat_timer.start()

        for process in process_list:
            process.start()
        chat_timer.stop("process.start()")
        
        chat_timer.start()
        for process in process_list:
            process.join()
        chat_timer.stop("process.join()")
        
        chat_timer.start()
        resulst_map = {}
        time_sum = 0
        while (not results_q.empty()):
            result_item = results_q.get()
            resulst_map[result_item[0]] = result_item[1]
            time_sum += result_item[2]
        
        output = f"\nNot only:\n {resulst_map['master']['output']}"
        output += '\n' + f"\nBut also:\n"
        output += resulst_map['instance'].get_data('output')
        output += resulst_map['instance_law'].get_data('output')
        chat_timer.stop("get output")
        print(f"[Test info]: time_sum = {time_sum:.2f} sec")

        print(f"output = {output}")

        chat_timer.start()
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant，把输入内容进行，保持感情基调"},
                {"role": "user", "content": output},
            ],
            stream=False
        ).choices[0].message.content
        chat_timer.stop("client.chat.completions")

        self.res_info = response
        print(f"response = {response}")
        return response

    def __deepcopy__(self, memo):
        # 创建一个新的 AgentDemo 实例
        new_agent_demo = type(self)()
        # 使用 deepcopy 递归复制所有属性
        for key, value in self.__dict__.items():
            if isinstance(value, (Agent, Master)):
                # 确保 Agent 和 Master 对象也能被深拷贝
                setattr(new_agent_demo, key, copy.deepcopy(value, memo))
            else:
                setattr(new_agent_demo, key, copy.deepcopy(value, memo))
        # print("new_agent_demo", new_agent_demo)
        return new_agent_demo

if __name__ == '__main__':
    x = AgentDemo()
    main_timer = Timer()
    for i in range(5):
        # Sample: 我不想学英语，我该怎么办呢
        user_input = input("请输入内容,如果想退出请输入停止: ")
        main_timer.start()
        print('user_input =',user_input)
        x.chat(user_input)
        main_timer.stop("Total time")
