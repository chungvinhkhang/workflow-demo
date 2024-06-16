import sys
from orchestration import Orchestration

def start_workflow_prompt(workflow_code):
    orches = Orchestration(workflow_code)
    arg_keys = orches.get_required_args()
    state = {}
    for arg_key in arg_keys:
        inp = input(f"Input {arg_key}: ")
        state[arg_key] = inp
    orches.start(state)
    orches.commit()

if __name__ == "__main__":
    workflow_code = sys.argv[1]
    start_workflow_prompt(workflow_code)
