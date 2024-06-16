import sys
from db import create_connection
from orchestration import Orchestration

def _get_my_tasks(user_id):
    conn = create_connection()
    with conn:
        res = conn.execute("SELECT id, title, desc, task_type, status FROM tasks WHERE assignee = ? and status <> 2", [user_id])
        all_tasks = res.fetchall()
        return all_tasks

def finish_manual_task(task_id):
    orches = Orchestration.from_task(task_id)
    orches.finish_task(task_id, only_manual=True)
    orches.commit()

def list_tasks(user_id):
    status_to_display = {0: "NO STARTED", 1: "IN PROGRESS", 2: "DONE"}
    tasks = _get_my_tasks(user_id)
    for row in tasks:
        print("id\t", row["id"])
        print("title\t", row["title"])
        print("desc\t", row["desc"])
        print("status\t", status_to_display.get(row["status"], ''))
        print("type\t", row["task_type"])
        if row["task_type"] == "MANUAL":
            print("CLI\t", f"python my_tasks.py {user_id} finish {row["id"]}")
        print("---------------")

if __name__ == "__main__":
    user_id = sys.argv[1]
    command = sys.argv[2]
    print(f"Logged in as: {user_id}")
    print("---------------")
    if command == "list":
        # CLI: my_tasks <user-id> list
        list_tasks(user_id)
    elif command == "finish":
        # CLI: my_tasks <user-id> finish <task-id>
        task_id = sys.argv[3]
        finish_manual_task(task_id)
        list_tasks(user_id)
