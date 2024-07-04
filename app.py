import config
from openai import OpenAI
import os
import subprocess
import json

# OpenAI client
openai_client = OpenAI(
    api_key=config.OPENAI_API_KEY,
)
CHATGPT_MODEL = "gpt-4o"

# 对话历史记录
conversation = []

# 初始化对话，告知格式要求
initial_messages = [
    {"role": "user", "content": "在Q&A的模式下，是否可以按照要求输出格式？比如，“问题”是一个“用户指令”，回答，以类似json格式的方式输出完成“用户指令”的shell脚本，具体来说，输出的“回答”，以这种方式：{answer:非脚本的解释性语言,action:[shell_1, shell_2,...]}(其中shell_n，是以文本格式呈现的完整脚本文件。"},
    {"role": "user", "content": '举例说明:用户指令：请显示当前目录；你回答：{"answer":"根据用户指令，生成shell脚本","actions":[{"shell": "ls -l"}]}'},
    {"role": "user", "content": '不需要再重复用户指令'},
    {"role": "user", "content": '不用加"json"'}
]

conversation.extend(initial_messages)

response = openai_client.chat.completions.create(
    model=CHATGPT_MODEL,
    messages=conversation
)

print(response.choices[0].message.content)
conversation.append({"role": "assistant", "content": response.choices[0].message.content})

# 获取用户命令
user_cmd = input("请输入您的指令:\n")
conversation.append({"role": "user", "content": user_cmd})

# 调用ChatGPT生成shell脚本
response = openai_client.chat.completions.create(
    model=CHATGPT_MODEL,
    messages=conversation
)

chatgpt_actions_str = response.choices[0].message.content
conversation.append({"role": "assistant", "content": chatgpt_actions_str})

print(chatgpt_actions_str)

# 解析并执行生成的shell脚本
actions = json.loads(chatgpt_actions_str).get("actions", [])
results = []

for action in actions:
    script = list(action.values())[0]
    result = subprocess.run(script, shell=True, capture_output=True, text=True)
    results.append({
        "script": script,
        "output": result.stdout,
        "error": result.stderr
    })

# 将执行结果发送回ChatGPT
execution_results = json.dumps(results, indent=2)
conversation.append({"role": "system", "content": execution_results})

response = openai_client.chat.completions.create(
    model=CHATGPT_MODEL,
    messages=conversation
)

final_response = response.choices[0].message.content
print(final_response)