import config
from openai import OpenAI
import os
import subprocess
import json

#openai client
openai_client = OpenAI(
    api_key=config.OPENAI_API_KEY
)
#first tell chatgpt the answers form as:
# json likes {action:[shell_1, shell_2,..]}
response = openai_client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role":"user", "content":"在Q&A的模式下，是否可以按照要求输出格式？比如，“问题”是一个“命令”，回答，以类似json格式的方式输出完成“命令”的shell脚本，具体来说，输出的“回答”，以这种方式：action:[shell_1, shell_2,...](其中shell_n，是以文本格式呈现的完整脚本文件。"},
        {"role":"user", "content":"我的意图是，我通过chatgpt API调用的方式，我向chatgpt发出指令，然后，chagpt根据指令，生成shell脚本，然后，我解析出脚本，交给后台服务进程或者调用chatgpt api的当前进程，去执行脚本， 指令，然后，再把执行结果返回给你chatgpt。同时有必要的话，也呈现给用户，或者等到chatgpt收到脚本执行结果之后，再生成回答，呈现给用户。"}
    ]
)
print(response.choices[0].message.content)

#get user's commans
user_cmd = input("请输入您的指令:\n")
chatgpt_actions_str = openai_client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role":"user","content":user_cmd}
    ]
)
#get action shell file
scripts = chatgpt_actions_str['action']
for script in scripts:
    for script_name, script_content in script.items():
        # 保存脚本到文件
        script_path = f"./{script_name}.sh"
        with open(script_path, "w") as script_file:
            script_file.write(script_content)

        # 给予执行权限
        os.chmod(script_path, 0o755)

        # 执行脚本
        result = subprocess.run([script_path], capture_output=True, text=True)

        # 获取执行结果
        output = result.stdout
        error = result.stderr
        returncode = result.returncode

        # 打印或处理执行结果
        print(f"Output: {output}")
        print(f"Error: {error}")
        print(f"Return Code: {returncode}")
        #tell chatgpt the result of shell execution
        result_shell_exe = f"Output: {output};" + f"Error: {error};" + f"Return Code: {returncode}"
        exe_res = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role":"sys","content":result_shell_exe}
            ]
        )
        print(exe_res.choices[0].message.content)