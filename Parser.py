import autogen
from autogen.agentchat.contrib.math_user_proxy_agent import MathUserProxyAgent
import easyocr

import json
from openai import OpenAI
client = OpenAI()

# 请将 openai.api_key 替换为你的实际 API 密钥


# AssistantAgent 初始化
config_list = [
    {
        'model': 'gpt-4o',
        'api_key': 'sk-proj-duozMzg3L6ardgQeu6g4T3BlbkFJcoPr49KLa9JqPVGitNk6',
        'stream': True,
    }
]

assistant = autogen.AssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant.",
    llm_config={
        "timeout": 300,
        "seed": 22,
        "config_list": config_list,
    }
)

mathproxyagent = MathUserProxyAgent(
    name="mathproxyagent",
    human_input_mode="NEVER",
    code_execution_config={"use_docker": False},
)


# 输入处理模块
def process_input(input_data, input_type='text'):
    if input_type == 'text':
        return input_data
    elif input_type == 'image':
        return recognize_text_from_image(input_data)
    else:
        raise ValueError("Unsupported input type")


def recognize_text_from_image(image_path):
    reader = easyocr.Reader(['ch_sim', 'en'])
    result = reader.readtext(image_path, detail=0)
    return ' '.join(result)


# 问题识别模块
def identify_problem_type(question):
    prompt = (
        f"请识别以下数学题的类型，并提取关键参数，格式为JSON：\n"
        f"问题：{question}\n"
        f"示例：\n"
        f"输入：计算 56 × 34 的结果。\n"
        f"输出：{{\"question_type\": \"multiplication\", \"operands\": [56, 34]}}\n"
        f"输入：求解方程 ax^2 + bx + c = 0 的解，其中 a=1, b=-3, c=2。\n"
        f"输出：{{\"question_type\": \"quadratic_equation\", \"coefficients\": {{\"a\": 1, \"b\": -3, \"c\": 2}}}}\n"
        f"问题：{question}"
    )

    response = client.chat.completions.create(
        engine="gpt-4",
        prompt=prompt,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.5
    )

    return response.choices[0].text.strip()


# 解析模块
def parse_problem(question):
    identified = identify_problem_type(question)
    try:
        parsed = json.loads(identified)
    except json.JSONDecodeError:
        parsed = {"error": "解析失败"}
    return parsed


# 验证模块
def validate_parsed_question(parsed_question):
    if "error" in parsed_question:
        return False
    if "question_type" not in parsed_question:
        return False
    if parsed_question["question_type"] == "multiplication":
        return "operands" in parsed_question
    if parsed_question["question_type"] == "quadratic_equation":
        return "coefficients" in parsed_question and all(k in parsed_question["coefficients"] for k in ["a", "b", "c"])
    if parsed_question["question_type"] == "geometry":
        return "shape" in parsed_question and "property" in parsed_question
    # 添加更多验证规则
    return True


# 生成Python代码
def generate_python_code(parsed_data):
    if parsed_data["question_type"] == "multiplication":
        operands = parsed_data["operands"]
        code = f"result = {operands[0]} * {operands[1]}"
    elif parsed_data["question_type"] == "quadratic_equation":
        coefficients = parsed_data["coefficients"]
        code = f"a = {coefficients['a']}\nb = {coefficients['b']}\nc = {coefficients['c']}\n# 使用公式计算解（此处省略具体计算步骤）"
    elif parsed_data["question_type"] == "geometry":
        shape = parsed_data["shape"]
        if shape == "circle":
            radius = parsed_data["radius"]
            code = f"import math\narea = math.pi * {radius} ** 2"
        # 添加更多问题类型的代码生成逻辑
    else:
        code = "# 暂不支持此类型问题的代码生成"
    return code


# 执行Python代码
def execute_python_code(code):
    local_vars = {}
    try:
        exec(code, {}, local_vars)
        return local_vars.get("result") or local_vars.get("area")  # 返回计算结果
    except Exception as e:
        return f"执行Python代码时出错：{str(e)}"


# 编程Agent
def programming_agent(problem):
    parsed_data = parse_problem(problem)
    if not validate_parsed_question(parsed_data):
        return "解析失败或结果无效"
    python_code = generate_python_code(parsed_data)
    result = execute_python_code(python_code)
    return result


# 讲解Agent
def explain(parsed_data, generated_code, result):
    explanation = ""
    if parsed_data["question_type"] == "multiplication":
        operands = parsed_data["operands"]
        explanation = f"我们有一个乘法题：{operands[0]} 乘以 {operands[1]}。"
        explanation += f"\n为了解决这个问题，我们生成了一个Python代码：\n{generated_code}"
        explanation += f"\n执行代码后，得到的结果是：{result}"
    elif parsed_data["question_type"] == "quadratic_equation":
        coefficients = parsed_data["coefficients"]
        explanation = f"我们有一个二次方程题：{coefficients['a']}x^2 + {coefficients['b']}x + {coefficients['c']} = 0。"
        explanation += f"\n为了解决这个问题，我们生成了一个Python代码：\n{generated_code}"
        explanation += f"\n执行代码后，得到的结果是：{result}（此处省略具体计算步骤）"
    elif parsed_data["question_type"] == "geometry" and parsed_data.get("shape") == "circle":
        radius = parsed_data["radius"]
        explanation = f"我们有一个几何题：求一个圆的面积，半径为 {radius}。"
        explanation += f"\n为了解决这个问题，我们生成了一个Python代码：\n{generated_code}"
        explanation += f"\n执行代码后，得到的结果是：{result}（单位^2）"
    else:
        explanation = "抱歉，我们暂时无法解释该类型的问题。"
    return explanation


def explanation_agent(problem):
    parsed_data = parse_problem(problem)
    if not validate_parsed_question(parsed_data):
        return "解析失败或结果无效"
    python_code = generate_python_code(parsed_data)
    result = execute_python_code(python_code)
    explanation = explain(parsed_data, python_code, result)
    return explanation


# 使用autogen框架解决数学问题
math_problems = [
    r"从 1、3、5、7、9中任取3个数，从 0、2、4、6、8中任取2个数，组成无重复数字的五位数共有(      )个。",
]

for problem in math_problems:
    parsed_data = parse_problem(problem)
    if not validate_parsed_question(parsed_data):
        print(f"解析失败或结果无效：{problem}")
        continue

    python_code = generate_python_code(parsed_data)
    result = execute_python_code(python_code)
    explanation = explain(parsed_data, python_code, result)

    mathproxyagent.initiate_chat(assistant, message=mathproxyagent.message_generator, problem=problem)

    print("问题:", problem)
    print("解析结果:", parsed_data)
    print("生成的代码:", python_code)
    print("计算结果:", result)
    print("详细讲解:", explanation)
