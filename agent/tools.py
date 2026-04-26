import json
from datetime import datetime
from typing import List, Dict, Any

# 导入数据库管理器
from memory.manager import TaskManager
# 导入数据校验模型
from models.task import TaskCreate, TaskResponse

# 工具定义的 JSON Schema 列表（告诉 DeepSeek 有哪些函数可以调用）
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",                    # 函数名称
            "description": "创建一个新的项目管理任务", # 功能描述，帮助模型判断何时调用
            "parameters": {                        # 参数定义，遵循 JSON Schema 规范
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "任务标题"
                    },
                    "description": {
                        "type": "string",
                        "description": "任务描述"
                    },
                    "deadline": {
                        "type": "string",
                        "description": "截止日期 (YYYY-MM-DD HH:MM)"
                    }
                },
                "required": ["title"]              # 必填参数
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "根据任务 ID 删除一个任务",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "要删除的任务 ID"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "列出所有任务，可以筛选未完成/已完成的任务",
            "parameters": {
                "type": "object",
                "properties": {
                    "completed": {
                        "type": "boolean",
                        "description": "是否只显示已完成的任务，不填则显示全部"
                    }
                },
                "required": []                     # 没有必填参数
            }
        }
    }
]
def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """
    根据 DeepSeek 传回的工具名称和参数，执行真实的数据库操作，
    并返回文本结果给模型。
    """
    # 使用 with 自动管理数据库连接
    with TaskManager() as tm:
        if tool_name == "add_task":
            # ---- 参数解析与校验 ----
            try:
                deadline = None
                # 如果参数中有 deadline 且非空，尝试转换为 datetime 对象
                if "deadline" in arguments and arguments["deadline"]:
                    deadline = datetime.fromisoformat(arguments["deadline"])
                # 用 Pydantic 校验并构造 TaskCreate 对象
                task_data = TaskCreate(
                    title=arguments["title"],
                    description=arguments.get("description", ""),
                    deadline=deadline
                )
            except Exception as e:
                # 如果校验失败，返回错误信息给模型
                return f"参数错误: {str(e)}"
            
            # ---- 写入数据库 ----
            task = tm.create_task(
                title=task_data.title,
                description=task_data.description,
                deadline=task_data.deadline
            )
            # 返回成功消息，包含任务 ID 方便后续操作
            return f"任务「{task.title}」创建成功，ID：{task.id}"

        elif tool_name == "list_tasks":
            # 获取筛选条件（如果有）
            completed = arguments.get("completed")
            # 查询数据库
            tasks = tm.list_tasks(completed=completed)
            # 如果没有任何任务，返回提示
            if not tasks:
                return "当前没有符合条件的任务。"
            # 构建格式化的任务列表
            task_lines = []
            for t in tasks:
                # 处理 deadline 的显示格式
                deadline_str = t.deadline.strftime("%Y-%m-%d %H:%M") if t.deadline else "无截止日期"
                # 用图标标记完成状态
                status = "✅" if t.is_completed else "⬜"
                # 组合成一行
                task_lines.append(f"{status} [{t.id}] {t.title} (截止: {deadline_str})")
            # 用换行符连接所有行
            return "\n".join(task_lines)
        elif tool_name == "delete_task":
            task_id = arguments.get("task_id")
            if task_id is None:
                return "错误：缺少 task_id 参数"
            success = tm.delete_task(task_id)
            if success:
                return f"任务 {task_id} 已成功删除"
            else:
                return f"任务 {task_id} 不存在"
        else:
            # 如果模型调用了未实现的工具，返回错误信息
            return f"未知工具: {tool_name}"