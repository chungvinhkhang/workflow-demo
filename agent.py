import sys
from orchestration import Orchestration

def finish_task(task_id):
    orches = Orchestration.from_task(task_id)
    orches.finish_task(task_id)
    orches.commit()

if __name__ == "__main__":
    task_id = sys.argv[1]
    finish_task(task_id)