import json
from openai import OpenAI
from config import config
from agent.tools import TOOL_DEFINITIONS,execute_tool

class ProjectAgent:
  def __init__(self):
    self.client = OpenAI(api_key=config.DEEPSEEK_API_KEY,base_url=config.DEEPSEEK_BASE_URL)
    self.tools = TOOL_DEFINITIONS
    self.message=[{"role": "system", "content": (
        "你是一个项目管理助手。请严格按照用户的指令操作。"
        "用户没有明确指定的字段（如描述、截止日期等）一律留空（不提供默认值），"
        "不要自行脑补缺失的信息。除非用户要求，否则不添加任何额外内容。"
        "请用中文回复。"
    )}]
  def run(self,user_input):
    self.message.append({"role": "user", "content": user_input})
    response=self.client.chat.completions.create(
      model=config.DEEPSEEK_MODEL,
      messages=self.message,
      tools=self.tools,
      tool_choice="auto"
    )
    response_message=response.choices[0].message
    self.message.append(response_message)
    if response_message.tool_calls:
      for tool_call in response_message.tool_calls:
        function_name=tool_call.function.name
        functioN_args=json.loads(tool_call.function.arguments)
        function_response=execute_tool(function_name,functioN_args)
        self.message.append({
          "tool_call_id": tool_call.id,
          "role": "tool",
          "name": function_name,
          "content": function_response
        })
      second_response=self.client.chat.completions.create(
        model=config.DEEPSEEK_MODEL,
        messages=self.message
      )
      final_response=second_response.choices[0].message.content
      self.message.append({"role":"assistant", "content": final_response})
      return final_response
    else:
      return response_message.content