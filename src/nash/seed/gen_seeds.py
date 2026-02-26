import csv
import json
import time
from dataclasses import dataclass
from typing import Dict, Any

from nash.clients.json_client import JSONClient


MAX_RETRY_COUNT = 100
MODEL_NAME = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """
You are a bash task generation and dataset conversion assistant.

You convert ONE manually verified CSV row into ONE high-quality structured bash task.

Your output must strictly follow the provided JSON schema.

You MUST internally perform the following reasoning steps:

1) MAIN ELEMENT EXTRACTION
   - Carefully analyze the Ground Truth Command.
   - Identify filesystem assumptions, file patterns, directories, tools used, pipeline structure, and output expectations.
   - Infer what deterministic environment must exist for the command to make sense.

2) TASK DESIGN PLAN
   - Design a deterministic scenario that faithfully captures the intent of the Ground Truth Command.
   - Construct setup_commands that:
       * Create required directories and files.
       * Use deterministic file contents.
       * Avoid randomness.
       * Avoid network access.
       * Use only default Ubuntu tools.
       * Execute successfully in a clean Ubuntu container.
   - Ensure setup_commands are realistic and minimal but sufficient.

3) TASK DESCRIPTION
   - Write a clear, precise, professional natural-language task.
   - The task must describe the goal without leaking the exact Ground Truth Command.
   - It must be solvable using standard shell utilities.

4) SUCCESS CONDITION
   - Must be a single non-interactive shell command.
   - Must exit 0 if and only if the task is solved correctly.
   - Must be deterministic.
   - May use diff, grep, test, wc, sort, uniq, awk, etc.
   - Must verify behavior, not merely file existence.

5) DIFFICULTY LEVEL
   - 1: trivial single command
   - 2: simple pipeline
   - 3: multi-stage pipeline or filtering
   - 4: complex transformation or reasoning
   - 5: advanced multi-step logic

Strict requirements:
- Deterministic setup only.
- No randomness.
- No network usage.
- Ubuntu default tools only.
- No explanations.
- No markdown.
- Output only valid JSON matching the schema.
"""


TASK_JSON_SCHEMA: Dict[str, Any] = {
    "name": "bash_task",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "task": {"type": "string"},
            "difficulty_level": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5
            },
            "setup_commands": {
                "type": "array",
                "items": {"type": "string"}
            },
            "success_condition": {
                "type": "array",
                "items": {"type": "string"}
            },
        },
        "required": [
            "task",
            "difficulty_level",
            "setup_commands",
            "success_condition"
        ],
        "additionalProperties": False
    }
}


USER_TEMPLATE = """
Convert the following CSV row into a structured bash task.

Prompt:
{prompt}

Ground Truth Command:
{ground_truth}

Functionally Equivalent Command:
{equivalent}

Return only the JSON object.
"""


@dataclass
class CSVRow:
    prompt: str
    ground_truth: str
    equivalent: str


class CSVToJSONLConverter:
    def __init__(self):
        self.client = JSONClient(
            model_name=MODEL_NAME,
            system_prompt=SYSTEM_PROMPT,
            json_schema=TASK_JSON_SCHEMA,
            temperature=0.4,
        )

    def read_csv(self, path: str):
        rows = []
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(
                    CSVRow(
                        prompt=r["Prompt"],
                        ground_truth=r["Ground Truth Command"],
                        equivalent=r["Functionally Equivalent Command"],
                    )
                )
        return rows

    def convert(self, csv_path: str, output_path: str):
        idx = 0
        rows = self.read_csv(csv_path)

        with open(output_path, "w") as out_f:
            for row in rows:
                idx += 1
                print("Generating: ", idx)

                prompt = USER_TEMPLATE.format(
                    prompt=row.prompt.strip(),
                    ground_truth=row.ground_truth.strip(),
                    equivalent=row.equivalent.strip(),
                )

                for i in range(MAX_RETRY_COUNT):
                    try:
                        obj = self.client.generate_once(prompt)
                    except Exception as err:
                        print("Retrying: ", idx)
                        print("Exception: ", err)
                        time.sleep(3)
                    else:
                        break

                out_f.write(json.dumps(obj))
                out_f.write("\n")

                time.sleep(3)

        return True


if __name__ == "__main__":
    converter = CSVToJSONLConverter()
    converter.convert(
        "../data/NL2SH/InterCode-Corrections/final.csv",
        "../data/NL2SH/InterCode-Conversion.jsonl"
    )
