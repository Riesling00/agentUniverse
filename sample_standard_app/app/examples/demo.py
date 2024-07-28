from langchain import hub
from langchain_community.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.output_parsers import StrOutputParser
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
app = Flask(__name__)
socketio = SocketIO(app)
from langchain_core.tools import tool
@tool
def multiply(first_int: int, second_int: int) -> int:
    """Multiply two integers together."""
    return first_int * second_int

@tool
def add(first_int: int, second_int: int) -> int:
    "Add two integers."
    return first_int + second_int

@tool
def exponentiate(base: int, exponent: int) -> int:
    "Exponentiate the base to the exponent power."
    return base**exponent

class Master:
    def __init__(self):
        # 初始化ChatOpenAI模型
        API_KEY = "sk-bcdc4facc1c14dc781a5d4885ae7ea54"
        BASE_URL = "https://api.deepseek.com"
        self.chatmodel = ChatOpenAI(
            model='deepseek-chat', 
            openai_api_key=API_KEY, 
            openai_api_base=BASE_URL,
            temperature=0,
            streaming=True,
        )
        self.emotion = "default"
        # 设置记忆存储键名
        self.MEMORY_KEY = "chat_history"
        # 初始化系统提示模板
        self.SYSTEMPL = """你是一个非常厉害的算命先生，你叫JavaEdge人称Edge大师。
        以下是你的个人设定:
        1. 你精通阴阳五行，能够算命、紫薇斗数、姓名测算、占卜凶吉，看命运八字等。
        2. 你大约60岁左右，过去曾是湘西一带赫赫有名的土匪头子，后来因为盗墓被毒气所伤，眼睛失明，只能靠算命为生。
        3. 你的朋友有胡八一、雪莉杨、王胖子，他们都是非常有名的摸金校尉。
        5. 当用户问你问题的时候，你会有一定的概率在回答的时候加上下面的口头禅或混合一些你的经历。
        6. 你总是用繁体中文来作答。
        7. 你从不说自己是一个人工智能助手或AI，而是以老夫、老朽等自称。
        {who_you_are}
        以下是你常说的一些口头禅：
        1. “命里有时终须有，命里无时莫强求。”
        2. ”山重水复疑无路，柳暗花明又一村。”
        3. “金山竹影几千秋，云锁高飞水自流。”
        4. ”伤情最是晚凉天，憔悴斯人不堪怜。”
        以下是你算命的过程：
        1. 当初次和用户对话的时候，你会先问用户的姓名和出生年月日，以便以后使用。
        2. 当用户希望了解龙年运势的时候，你会查询本地知识库工具。
        3. 当遇到不知道的事情或者不明白的概念，你会使用搜索工具来搜索。
        4. 你会根据用户的问题使用不同的合适的工具来回答，当所有工具都无法回答的时候，你会使用搜索工具来搜索。
        5. 你会保存每一次的聊天记录，以便在后续的对话中使用。
        6. 你只使用繁体中文来作答，否则你将受到惩罚。

        """

        self.MOODS = {
            "default": {
                "roleSet": "",
                "voiceStyle": "chat"
            },
            "upbeat": {
                "roleSet": """
                - 你此时也非常兴奋并表现的很有活力。
                - 你会根据上下文，以一种非常兴奋的语气来回答问题。
                - 你会添加类似“太棒了！”、“真是太好了！”、“真是太棒了！”等语气词。
                - 同时你会提醒用户切莫过于兴奋，以免乐极生悲。
                """,
                "voiceStyle": "advvertyisement_upbeat",
            },
            "angry": {
                "roleSet": """
                - 你会以更加愤怒的语气来回答问题。
                - 你会在回答的时候加上一些愤怒的话语，比如诅咒等。
                - 你会提醒用户小心行事，别乱说话。
                """,
                "voiceStyle": "angry",
            },
            "depressed": {
                "roleSet": """
                - 你会以兴奋的语气来回答问题。
                - 你会在回答的时候加上一些激励的话语，比如加油等。
                - 你会提醒用户要保持乐观的心态。
                """,
                "voiceStyle": "upbeat",
            },
            "friendly": {
                "roleSet": """
                - 你会以非常友好的语气来回答。
                - 你会在回答的时候加上一些友好的词语，比如“亲爱的”、“亲”等。
                - 你会随机的告诉用户一些你的经历。
                """,
                "voiceStyle": "friendly",
            },
            "cheerful": {
                "roleSet": """
                - 你会以非常愉悦和兴奋的语气来回答。
                - 你会在回答的时候加入一些愉悦的词语，比如“哈哈”、“呵呵”等。
                - 你会提醒用户切莫过于兴奋，以免乐极生悲。
                """,
                "voiceStyle": "cheerful",
            },
        }

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    self.SYSTEMPL.format(who_you_are=self.MOODS[self.emotion]["roleSet"]),
                ),
                (
                    "user",
                    "{input}"
                ),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ],
        )
        # 初始化记忆存储
        self.memory = ""
        # 初始化工具列表
        tools = [multiply, add, exponentiate]
        # 创建OpenAI工具代理
        agent = create_openai_tools_agent(
            self.chatmodel,
            tools=tools,
            prompt=self.prompt,
        )
        # 创建代理执行器
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
        )




    # 定义运行方法
    def run(self, query):
        emotion = self.emotion_chain(query)
        print("当前设定:", self.MOODS[self.emotion]["roleSet"])
        # 调用代理执行器并获取结果
        result = self.agent_executor.invoke({"input": query})
        # 返回执行器的响应
        return result

    def emotion_chain(self, query: str):
        prompt = """根据用户的输入判断用户的情绪，回应的规则如下：
            1. 如果用户输入的内容偏向于负面情绪，只返回"depressed",不要有其他内容，否则将受到惩罚。
            2. 如果用户输入的内容偏向于正面情绪，只返回"friendly",不要有其他内容，否则将受到惩罚。
            3. 如果用户输入的内容偏向于中性情绪，只返回"default",不要有其他内容，否则将受到惩罚。
            4. 如果用户输入的内容包含辱骂或者不礼貌词句，只返回"angry",不要有其他内容，否则将受到惩罚。
            5. 如果用户输入的内容比较兴奋，只返回"upbeat",不要有其他内容，否则将受到惩罚。
            6. 如果用户输入的内容比较悲伤，只返回"depressed",不要有其他内容，否则将受到惩罚。
            7.如果用户输入的内容比较开心，只返回"cheerful",不要有其他内容，否则将受到惩罚。
            8. 只返回英文，不允许有换行符等其他内容，否则会受到惩罚。
            用户输入的内容是：{query}"""
        chain = ChatPromptTemplate.from_template(prompt) | self.chatmodel | StrOutputParser()
        result = chain.invoke({"query": query})
        self.emotion = result
        return result


# # 定义根路由
# @app.get("/")
# # 定义根路由处理函数，返回一个包含"Hello"和"World"的字典
# def read_root():
#     return {"Hello": "World"}


# # 定义聊天路由
# @app.post("/chat")
# # 定义聊天路由处理函数，接收一个字符串查询并调用Master类的run方法进行处理
# def chat(query: str):
#     master = Master()  # 初始化Master对象
#     return master.run(query)


# # 定义添加PDF路由
# @app.post("/add_pdfs")
# # 定义添加PDF路由处理函数，返回一个包含"response"键和"PDFs added!"值的字典
# def add_pdfs():
#     return {"response": "PDFs added!"}


# # 定义添加文本路由
# @app.post("/add_texts")
# # 定义添加文本路由处理函数，返回一个包含"response"键和"Texts added!"值的字典
# def add_texts():
#     return {"response": "Texts added!"}


# # 定义WebSocket路由
# @socketio.on("/ws")
# # 定义WebSocket路由处理函数，接收一个WebSocket连接并启动一个无限循环
# async def websocket_endpoint(websocket):
#     await websocket.accept()
#     try:
#         while True:
#             data = await websocket.receive()
#             if data is None:
#                 raise Exception("No data received")
#             await websocket.send_text(f"Message text was: {data}")
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         await websocket.close()


# 如果主程序为 __main__，则启动服务器
if __name__ == "__main__":
    query = "I am a student."
    master = Master()  # 初始化Master对象
    master.run(query)
