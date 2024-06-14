import autogen
from autogen.agentchat.contrib.math_user_proxy_agent import MathUserProxyAgent
import os
config_list = [
    {
        'model': 'gpt-4o',
        'api_key': 'sk-proj-duozMzg3L6ardgQeu6g4T3BlbkFJcoPr49KLa9JqPVGitNk6',  # 用于测试的API key
        'stream': True,
    }
]

assistant = autogen.AssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant. Can solve math problems and give useful suggestions to users."
                   " Make sure that your output is Chinese",
    llm_config={
        "timeout": 300,
        "seed": 22,  # 这个参数没什么关系
        "config_list": config_list,
    }
)

mathproxyagent = MathUserProxyAgent(
    name="mathproxyagent",
    human_input_mode="ALWAYS",  # 交互输入模式，参考两个agent里的设定
    code_execution_config={"use_docker": False},
)

if "WOLFRAM_ALPHA_APPID" not in os.environ:
    os.environ["WOLFRAM_ALPHA_APPID"] = open("wolfram.txt").read().strip()


# List of math problems
math_problem = [r"已知实数x,y 满足3x ^ { 2 } + 2y ^ { 2 } = 6x，求x ^ { 2 } + y ^ {2}的最大值"]  # 数学问题问题传入

# Iterate over the list of math problems and solve each one
for problem in math_problem:
    mathproxyagent.initiate_chat(
        assistant,
        message=mathproxyagent.message_generator,
        problem=problem,
        prompt_type="two_tools")
