import sqlite3
DB_NAME = "workflow-demo.db"

def create_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect(DB_NAME)
    with conn:
        cur = conn.cursor()
        cur.execute("CREATE TABLE wf_instances(id INTEGER PRIMARY KEY AUTOINCREMENT, workflow_code TEXT, current_step TEXT, status INTEGER, state TEXT)")
        cur.execute("CREATE TABLE tasks(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, desc TEXT, wf_instance_id INTEGER, task_type TEXT, assignee INTEGER, status INTEGER)")
        cur.execute("CREATE INDEX idx_assignee_status ON tasks(assignee, status)")

if __name__ == "__main__":
    init_db()
