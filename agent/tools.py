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
            "description": (
            "创建一个新的任务。参数必须使用："
            "title（任务标题，必填），"
            "description（任务描述，可选），"
            "deadline（截止日期，格式YYYY-MM-DD，可选），"
            "parent_id（父任务ID，整数，可选）。"
            "注意：参数名必须严格为 title, description, deadline, parent_id。"
        ),
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
                    },
                    "parent_id": {
                        "type": "integer",
                        "description": "父任务 ID,如果要创建子任务"
                    }
                },
                "required": ["title"]              # 必填参数
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "以树形结构列出所有任务",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
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
        "name": "get_current_time",
        "description": "获取当前的日期和时间，用于判断截止日期、计算时间差等",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
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
                parent_id=arguments.get("parent_id")
                # 用 Pydantic 校验并构造 TaskCreate 对象
                task_data = TaskCreate(
                    title=arguments["title"],
                    description=arguments.get("description", ""),
                    deadline=deadline,
                    parent_id=parent_id
                )
            except Exception as e:
                # 如果校验失败，返回错误信息给模型
                return f"参数错误: {str(e)}"
            
            # ---- 写入数据库 ----
            task = tm.create_task(
                title=task_data.title,
                description=task_data.description,
                deadline=task_data.deadline,
                parent_id=parent_id
            )
            if parent_id:
                parent_task=tm.get_task(parent_id)
                parent_title=parent_task.title if parent_task else "未知父任务"
                return f"子任务 {task.id} 已成功创建，属于父任务 {parent_id} ({parent_title})"
            else:
                return f"任务{task.title}创建成功,ID:{task.id}"

        elif tool_name == "list_tasks":
            roots=tm.get_task_tree()
            if not roots:
                return "没有可显示的任务。"
            def format_tree(task,indent=0):
                lines=[]
                indent_str=" "*indent
                status_icon=( "✅" if task.is_completed else "⬜")
                deadline_str=task.deadline.strftime("%Y-%m-%d %H:%M") if task.deadline else "无截止日期"
                folder_icon="📁" if task.children_id else "  "
                lines.append(f"{indent_str}{folder_icon} {status_icon} [{task.id}] {task.title} (截至:{deadline_str})")
                for child in task.children_id:
                    lines.extend(format_tree(child,indent+1))
                return lines
            output=[]
            for root in roots:
                output.extend(format_tree(root))
            return "\n".join(output)
        elif tool_name == "delete_task":
            task_id = arguments.get("task_id")
            if task_id is None:
                return "错误：缺少 task_id 参数"
            success = tm.delete_task(task_id)
            if success:
                return f"任务 {task_id} 已成功删除"
            else:
                return f"任务 {task_id} 不存在"
        elif tool_name == "get_current_time":
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return f"当前时间是: {now}" 
        else:
            # 如果模型调用了未实现的工具，返回错误信息
            return f"未知工具: {tool_name}"