import random
import threading
import time

import gradio as gr
from rag_chat_bot import *
import os
import copy
STREAM_INTERVAL = 0.2
os.environ["no_proxy"] = "localhost,127.0.0.1,::1"

def gen_guiding_button_clicked(aign, user_input, res_info):
    print("res_info", res_info)
    aign.res_info = res_info
    aign.user_input = user_input
    print("user_input", user_input)
    gen_setting_thread = threading.Thread(target=aign.chat)
    gen_setting_thread.start()

    while gen_setting_thread.is_alive():
        yield [
            aign,
            aign.user_input,
            gr.Button(visible=True),
        ]
        time.sleep(STREAM_INTERVAL)
    yield [
        aign,
        aign.res_info,
    ]


if __name__ == "__main__":
    css = """
    #row1 {
        min-width: 200px;
        max-height: 700px;
        overflow: auto;
    }
    #row2 {
        min-width: 300px;
        max-height: 700px;
        overflow: auto;
    }
    #row3 {
        min-width: 200px;
        max-height: 700px;
        overflow: auto;
    }
    """

    with gr.Blocks(css=css) as demo:
        gr.Markdown("## AI 教育聊天客服 Demo")
        aign = gr.State(AgentDemo())
       
        with gr.Row():
            with gr.Column(scale=0, elem_id="row1"):
                with gr.Tab("开始"):
                    user_idea_text = gr.Textbox(
                        "我不想学英语，我该怎么办呢",
                        label="请输入内容,如果想退出请输入停止",
                        lines=4,
                        interactive=True,
                    )
                    gen_guiding_button = gr.Button("发送")
            with gr.Column(scale=3, elem_id="row2"):
                chatBox = gr.Chatbot(height=f"80vh", label="输出")

        print(f"\start:\n")
        gen_guiding_button.click(
            gen_guiding_button_clicked,
            [aign, user_idea_text, chatBox],
            [aign, chatBox],
        )

    demo.queue()
    demo.launch(share=True)