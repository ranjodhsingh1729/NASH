import json
import time
from dataclasses import dataclass

from nash.sandbox.sandbox import Sandbox
from nash.generation.prompts import (
    GENERATOR_SYSTEM_PROMPT,
    GENERATOR_JSON_SCHEMA,
    GENERATOR_USER_PROMPT_TEMPLATE as GENERATOR_USER_PROMPT,
    SOLVER_SYSTEM_PROMPT,
    SOLVER_JSON_SCHEMA,
    SOLVER_USER_PROMPT_TEMPLATE as SOLVER_USER_PROMPT
)
from nash.clients.json_client import JSONClient


MAX_RETRY_COUNT = 100
MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"


@dataclass
class Task:
    difficulty: int
    description: str
    setup_command: str
    success_condition: str

@dataclass
class Solution:
    reasoning: str
    solution_command: str


class Generator:
    def __init__(
        self,
        seed_path: str,
        task_path: str,
        multiplier = 100
    ):
        self.seeds = []
        self.task_path = task_path
        self.multiplier = multiplier
        self.client = JSONClient(
            model_name=MODEL_NAME,
            system_prompt=GENERATOR_SYSTEM_PROMPT,
            json_schema=GENERATOR_JSON_SCHEMA,
        )

        self.read_seeds(seed_path)

    def read_seed(self, seed_str: str):
        seed = json.loads(seed_str)
        if seed is None:
            return None
        else:
            return Task(
                seed.get("difficulty_level"),
                seed.get("task"),
                seed.get("setup_commands"),
                seed.get("success_condition")
            )

    def read_seeds(self, path: str):
        with open(path, "r") as fhand:
            for line in fhand:
                seed = self.read_seed(line)
                if seed is not None:
                    self.seeds.append(seed)

    def write_task(self, task: Task):
        with open(self.task_path, "a") as fhand:
            fhand.write(json.dumps(task.__dict__) + "\n")

    def write_tasks(self, tasks: list[Task]):
        for task in tasks:
            self.write_task(task)

    def generate_one(self, index: int):
        if index + 1 >= len(self.seeds):
            return None

        seed1 = self.seeds[index]
        seed2 = self.seeds[index + 1]

        prompt = GENERATOR_USER_PROMPT.format(
            task_1=seed1.description,
            setup_1=seed1.setup_command,
            success_1=seed1.success_condition,
            task_2=seed2.description,
            setup_2=seed2.setup_command,
            success_2=seed2.success_condition,
        )

        response = None
        for _ in range(MAX_RETRY_COUNT):
            try:
                response = self.client.generate_once(prompt)
            except Exception as e:
                print(self.client.client.api_key)
                print(e)
                print("Generation Retrying...")
                time.sleep(3)
            else:
                break

        if response is None:
            return None

        return Task(
            response.get("difficulty_level"),
            response.get("task"),
            " && ".join(response.get("setup_commands") or []),
            " && ".join(response.get("success_condition") or []),
        )

    def generate(self, offset):
        num_seeds = len(self.seeds)
        for i in range(offset, num_seeds - 1):
            for _ in range(self.multiplier):
                print("Generating Task: ", i, _)

                task = self.generate_one(i)
                if task is None:
                    print("Failed Generation: ", i, _)
                    continue

                self.write_task(task)


class Solver:
    def __init__(self, max_steps: int = 10):
        self.max_steps = max_steps
        self.client = JSONClient(
            model_name=MODEL_NAME,
            system_prompt=SOLVER_SYSTEM_PROMPT,
            json_schema=SOLVER_JSON_SCHEMA
        )

    def solve(self, task: Task, sandbox: Sandbox):
        steps = 0
        history = ""

        setup_result = sandbox.exec_shell(task.setup_command)
        if setup_result.returncode != 0:
            return False, history

        while steps < self.max_steps:
            prompt = SOLVER_USER_PROMPT.format(
                task=task.description,
                history=history
            )

            response = self.client.generate_once(prompt)
            solution = Solution(
                response.get("reasoning"),
                response.get("command")
            )

            result = sandbox.exec_shell(solution.solution_command)

            history += "\n".join(
                [
                    f"$ {solution.solution_command}",
                    f"EXIT CODE:{result.returncode}",
                    f"STDOUT:\n{result.stdout}",
                    f"STDERR:\n{result.stderr}",
                    "\n",
                ]
            )

            if result.returncode != 0:
                steps += 1
                continue

            check = sandbox.exec_shell(task.success_condition)
            if check.returncode == 0:
                return True, history

            steps += 1

        return False, history


if __name__ == "__main__":
    generator = Generator(
        "../data/NL2SH/InterCode-Conversion.jsonl",
        "../data/generated_tasks.jsonl"
    )

    offset = int(input("Enter Seed Offset: "))
    generator.generate(offset)
