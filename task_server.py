import asyncio
import json
from mcp.server import Server
from mcp.types import Tool, TextContent

# Sample task database
TASKS_DB = {
    "emp001": {
        "employee_id": "emp001",
        "name": "Alice Johnson",
        "role": "Developer",
        "tasks": [
            {"id": "t1", "title": "Fix login bug", "status": "completed"},
            {"id": "t2", "title": "Review PR #234", "status": "completed"},
            {"id": "t3", "title": "Update documentation", "status": "completed"},
            {"id": "t4", "title": "Refactor API endpoints", "status": "in_progress"},
            {"id": "t5", "title": "Write unit tests", "status": "pending"},
            {"id": "t6", "title": "Deploy to staging", "status": "pending"},
            {"id": "t7", "title": "Database optimization", "status": "pending"},
            {"id": "t8", "title": "Security audit", "status": "pending"},
            {"id": "t9", "title": "Performance testing", "status": "pending"},
            {"id": "t10", "title": "Code cleanup", "status": "pending"},
        ]
    },
    "emp002": {
        "employee_id": "emp002",
        "name": "Bob Smith",
        "role": "Designer",
        "tasks": [
            {"id": "t11", "title": "Design new logo", "status": "completed"},
            {"id": "t12", "title": "Create mockups", "status": "in_progress"},
            {"id": "t13", "title": "User research", "status": "pending"},
        ]
    },
    "emp003": {
        "employee_id": "emp003",
        "name": "Carol White",
        "role": "Manager",
        "tasks": [
            {"id": "t14", "title": "Team meeting", "status": "completed"},
            {"id": "t15", "title": "Budget review", "status": "in_progress"},
            {"id": "t16", "title": "Hiring plan", "status": "pending"},
        ]
    },
    "emp004": {
        "employee_id": "emp004",
        "name": "David Brown",
        "role": "QA Engineer",
        "tasks": [
            {"id": "t17", "title": "Test login flow", "status": "completed"},
            {"id": "t18", "title": "Regression testing", "status": "in_progress"},
            {"id": "t19", "title": "Bug reporting", "status": "pending"},
        ]
    },
    "emp005": {
        "employee_id": "emp005",
        "name": "Eve Davis",
        "role": "DevOps",
        "tasks": [
            {"id": "t20", "title": "Setup CI/CD", "status": "completed"},
            {"id": "t21", "title": "Monitor servers", "status": "in_progress"},
            {"id": "t22", "title": "Backup configuration", "status": "pending"},
        ]
    }
}


def get_task_summary(tasks):
    """Calculate task statistics"""
    completed = sum(1 for t in tasks if t["status"] == "completed")
    in_progress = sum(1 for t in tasks if t["status"] == "in_progress")
    pending = sum(1 for t in tasks if t["status"] == "pending")

    return {
        "total_tasks": len(tasks),
        "completed": completed,
        "in_progress": in_progress,
        "pending": pending
    }


# Create MCP server
app = Server("task-management")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_employee_tasks",
            description="Get all tasks for a specific employee by their ID (emp001-emp005)",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": "Employee ID (e.g., emp001, emp002, etc.)"
                    }
                },
                "required": ["employee_id"]
            }
        ),
        Tool(
            name="get_all_employees_summary",
            description="Get a summary of task completion for all employees",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_employee_by_name",
            description="Find an employee by their name and get their tasks",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Employee name (e.g., Alice, Bob, etc.)"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="get_pending_tasks",
            description="Get all pending tasks across all employees or for a specific employee",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": "Optional: Employee ID to filter by (e.g., emp001)"
                    }
                }
            }
        ),
        Tool(
            name="update_task_status",
            description="Update the status of a specific task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID (e.g., t1, t2, etc.)"
                    },
                    "new_status": {
                        "type": "string",
                        "description": "New status for the task",
                        "enum": ["pending", "in_progress", "completed"]
                    }
                },
                "required": ["task_id", "new_status"]
            }
        ),
        Tool(
            name="update_task_title",
            description="Update the title of a specific task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID (e.g., t1, t2, etc.)"
                    },
                    "new_title": {
                        "type": "string",
                        "description": "New title for the task"
                    }
                },
                "required": ["task_id", "new_title"]
            }
        ),
        Tool(
            name="add_task",
            description="Add a new task to an employee",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": "Employee ID (e.g., emp001)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title"
                    },
                    "status": {
                        "type": "string",
                        "description": "Task status (default: pending)",
                        "enum": ["pending", "in_progress", "completed"]
                    }
                },
                "required": ["employee_id", "title"]
            }
        ),
        Tool(
            name="delete_task",
            description="Delete a specific task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID to delete (e.g., t1, t2, etc.)"
                    }
                },
                "required": ["task_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""

    if name == "get_employee_tasks":
        employee_id = arguments["employee_id"]
        if employee_id not in TASKS_DB:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Employee {employee_id} not found"})
            )]

        employee = TASKS_DB[employee_id]
        result = {
            "employee_id": employee["employee_id"],
            "name": employee["name"],
            "role": employee["role"],
            "summary": get_task_summary(employee["tasks"]),
            "tasks": employee["tasks"]
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "get_all_employees_summary":
        summary = []
        for emp_id, employee in TASKS_DB.items():
            summary.append({
                "employee_id": emp_id,
                "name": employee["name"],
                "role": employee["role"],
                "summary": get_task_summary(employee["tasks"])
            })
        return [TextContent(type="text", text=json.dumps(summary, indent=2))]

    elif name == "get_employee_by_name":
        name_query = arguments["name"].lower()
        for emp_id, employee in TASKS_DB.items():
            if name_query in employee["name"].lower():
                result = {
                    "employee_id": employee["employee_id"],
                    "name": employee["name"],
                    "role": employee["role"],
                    "summary": get_task_summary(employee["tasks"]),
                    "tasks": employee["tasks"]
                }
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"No employee found with name '{arguments['name']}'"})
        )]

    elif name == "get_pending_tasks":
        employee_id = arguments.get("employee_id")
        pending_tasks = []

        if employee_id:
            if employee_id not in TASKS_DB:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": f"Employee {employee_id} not found"})
                )]
            employees = {employee_id: TASKS_DB[employee_id]}
        else:
            employees = TASKS_DB

        for emp_id, employee in employees.items():
            for task in employee["tasks"]:
                if task["status"] == "pending":
                    pending_tasks.append({
                        "employee_id": emp_id,
                        "employee_name": employee["name"],
                        "task_id": task["id"],
                        "title": task["title"]
                    })

        return [TextContent(type="text", text=json.dumps(pending_tasks, indent=2))]

    elif name == "update_task_status":
        task_id = arguments["task_id"]
        new_status = arguments["new_status"]

        # Find the task
        for emp_id, employee in TASKS_DB.items():
            for task in employee["tasks"]:
                if task["id"] == task_id:
                    old_status = task["status"]
                    task["status"] = new_status
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "success": True,
                            "message": f"Task '{task['title']}' status updated from '{old_status}' to '{new_status}'",
                            "task": task,
                            "employee": employee["name"]
                        }, indent=2)
                    )]

        return [TextContent(
            type="text",
            text=json.dumps({"error": f"Task {task_id} not found"})
        )]

    elif name == "update_task_title":
        task_id = arguments["task_id"]
        new_title = arguments["new_title"]

        # Find the task
        for emp_id, employee in TASKS_DB.items():
            for task in employee["tasks"]:
                if task["id"] == task_id:
                    old_title = task["title"]
                    task["title"] = new_title
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "success": True,
                            "message": f"Task title updated from '{old_title}' to '{new_title}'",
                            "task": task,
                            "employee": employee["name"]
                        }, indent=2)
                    )]

        return [TextContent(
            type="text",
            text=json.dumps({"error": f"Task {task_id} not found"})
        )]

    elif name == "add_task":
        employee_id = arguments["employee_id"]
        title = arguments["title"]
        status = arguments.get("status", "pending")

        if employee_id not in TASKS_DB:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Employee {employee_id} not found"})
            )]

        # Generate new task ID
        all_task_ids = []
        for employee in TASKS_DB.values():
            for task in employee["tasks"]:
                task_num = int(task["id"][1:])
                all_task_ids.append(task_num)
        new_task_id = f"t{max(all_task_ids) + 1}"

        new_task = {
            "id": new_task_id,
            "title": title,
            "status": status
        }

        TASKS_DB[employee_id]["tasks"].append(new_task)

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": f"New task added to {TASKS_DB[employee_id]['name']}",
                "task": new_task
            }, indent=2)
        )]

    elif name == "delete_task":
        task_id = arguments["task_id"]

        # Find and delete the task
        for emp_id, employee in TASKS_DB.items():
            for i, task in enumerate(employee["tasks"]):
                if task["id"] == task_id:
                    deleted_task = employee["tasks"].pop(i)
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "success": True,
                            "message": f"Task '{deleted_task['title']}' deleted from {employee['name']}'s tasks",
                            "deleted_task": deleted_task
                        }, indent=2)
                    )]

        return [TextContent(
            type="text",
            text=json.dumps({"error": f"Task {task_id} not found"})
        )]

    return [TextContent(
        type="text",
        text=json.dumps({"error": f"Unknown tool: {name}"})
    )]


async def main():
    """Run the server"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())