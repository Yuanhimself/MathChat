import io

from IPython.display import display
from PIL import Image
import pandas as pd

import autogen
from autogen.agentchat import AssistantAgent, UserProxyAgent
from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent
from openai import OpenAI
import os
import base64


config_list = [
    {
        'model': 'gpt-4o',
        'api_key': 'sk-proj-duozMzg3L6ardgQeu6g4T3BlbkFJcoPr49KLa9JqPVGitNk6',
        'stream': True,
    }
]

# Initiate an agent equipped with code interpreter
gpt_assistant = GPTAssistantAgent(
    name="Coder Assistant",
    llm_config={
        "config_list": config_list,
    },
    assistant_config={
        "tools": [{"type": "code_interpreter"}],
    },
    instructions="你是解决数学问题的专家。编写代码并运行它来解决数学问题。当任务解决并且没有问题时，回复 TERMINATE。",
)

user_proxy = UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda msg: "TERMINATE" in msg["content"],
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
    },
    human_input_mode="NEVER",
)


# When all is set, initiate the chat.
user_proxy.initiate_chat(
    gpt_assistant, message=r"f ( x ) = \frac { a ^ { 4 } + 5x ^ { 2 } + 16 } { x ^ { 2 } }最小值为？"
)
#gpt_assistant.delete_assistant()