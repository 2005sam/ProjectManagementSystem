import json
from openai import OpenAI
from config import config

class ProjectAgent:
  def __init__(self):
    self.client = OpenAI(api_key=config.DEEPSEEK_API_KEY,base_url=config.DEEPSEEK_BASE_URL)
    self.tools=self._get_tools()
    self.message=[{"role": "system", "content": "你是一个专业的项目管理助手，可以管理任务、文件等。"}]
  def _get_tools(self):
    return [
      {
        "type":"function",
        "function":{
          "name":"add_task",
          "description":"添加任务",
          "parameters":{
            "type":"object",
            "properties":{
              "title": {"type":"string","description":"任务标题"},
              "description": {"type":"string","description":"任务描述"},
              "due_date": {"type":"string","description":"任务截止日期(yyyy-mm-dd)"}
            },
            "required":["title"]
          }
        }
      }]
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
        function_name=tool_call.name
        functioN_args=json.loads(tool_call.function.arguments)
        if function_name=="add_task":
          function_response=f"任务 '{functioN_args['title']}' 已添加。"
        else:
          function_response=f"错误:未知的工具 '{function_name}'。"
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