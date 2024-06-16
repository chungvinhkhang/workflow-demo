import os
import json
from string import Template
from db import create_connection

GLOBAL_STATE = {
    "LMS_BASE_URL": "http://my-corp-lms.local"
}

class Orchestration:
    def __init__(self, workflow_code):
        self._workflow_code = workflow_code
        self._conn = None
        with open(os.path.join("workflows", f"{workflow_code}.json"), 'r') as stream:
            json_content = stream.read()
            self._workflow_definition = json.loads(json_content)

    @classmethod
    def from_task(cls, task_id):
        conn = create_connection()
        with conn:
            workflow = conn.execute("SELECT workflow_code FROM wf_instances WHERE id IN (SELECT wf_instance_id FROM tasks WHERE id = ?)", [task_id]).fetchone()
        if not workflow:
            raise Exception("Not found")
        return Orchestration(workflow["workflow_code"])

    def get_required_args(self):
        return self._workflow_definition.get("args", [])

    def start(self, state):
        entry_step_key = self._workflow_definition["entry"]
        params = [self._workflow_code, entry_step_key, json.dumps(state)]
        cursor = self._create_connection().cursor()
        cursor.execute("INSERT INTO wf_instances(workflow_code, current_step, status, state) VALUES(?, ?, 0, ?)", params)
        wf_instance_id = cursor.lastrowid
        self._create_task(entry_step_key, wf_instance_id, state)

    def _create_task(self, step, wf_instance_id, state):
        merged_state = {**GLOBAL_STATE, **state}
        task = self._workflow_definition["steps"][step]
        params = [Template(task["title"]).safe_substitute(merged_state), 
                Template(task["desc"]).safe_substitute(merged_state),
                wf_instance_id, 
                Template(task["task_type"]).safe_substitute(merged_state), 
                Template(task["assignee"]).safe_substitute(merged_state)]
        cursor = self._create_connection().cursor()
        cursor.execute("INSERT INTO tasks(title, desc, wf_instance_id, task_type, assignee, status) VALUES(?, ?, ?, ?, ?, 0)", params)
        if "$wf_task_id" in task["desc"]:
            wf_task_id = cursor.lastrowid
            new_desc = Template(task["desc"]).safe_substitute({**merged_state, "wf_task_id": wf_task_id})
            cursor.execute("UPDATE tasks SET desc = ? WHERE id = ?", [new_desc, wf_task_id])

    def finish_task(self, task_id, only_manual=False):
        cursor = self._create_connection().cursor()
        sql = ("SELECT tas.id, tas.assignee, tas.wf_instance_id, wfi.state, wfi.workflow_code, wfi.current_step "
            "FROM tasks tas INNER JOIN wf_instances wfi ON tas.wf_instance_id = wfi.id "
            "WHERE tas.id = ? and tas.status <> 2")
        if only_manual:
            sql += " AND tas.task_type = 'MANUAL'"
        task = cursor.execute(sql, [task_id]).fetchone()
        if not task:
            raise Exception("Not found")
        cursor.execute("UPDATE tasks SET status = 2 WHERE id = ? and status <> 2", [task["id"]])
        next_step_key = self._workflow_definition["steps"][task["current_step"]].get("next_step", None)
        if next_step_key:
            cursor.execute("UPDATE wf_instances SET current_step = ? WHERE id = ? and status <> 2", [next_step_key, task["wf_instance_id"]])
            self._create_task(next_step_key, task["wf_instance_id"], json.loads(task["state"] or "{}"))
        else:
            cursor.execute("UPDATE wf_instances SET status = 2 WHERE id = ? and status <> 2", [task["wf_instance_id"]])

    def commit(self):
        self._conn.commit()
        self._conn.close()

    def _create_connection(self):
        if self._conn is None:
            self._conn = create_connection()
        return self._conn