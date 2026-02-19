"""
Inspired By:
https://arxiv.org/pdf/2507.23751
https://github.com/deathbyknowledge/sos
"""

import json
from dataclasses import dataclass
from nash.clients.cloud_client import CloudClient
from nash.generation.prompts import GENERATOR_SYSTEM_PROMPT, GENERATOR_USER_PROMPT


MODEL_NAME = "openai/gpt-oss-120b"
MODEL_NAME = "llama-3.3-70b-versatile"


@dataclass  
class Task:
  dificulty: int
  description: str
  setup_command: str
  success_condition: str

@dataclass
class Solution:
  reasoning: str
  solution_command: str


class Generator:
  def __init__(self, seeds: list[Task]):
    self.seeds = seeds
    self.system_prompt = GENERATOR_SYSTEM_PROMPT
    self.client = CloudClient(
      model_name=MODEL_NAME, system_prompt=self.system_prompt
    )

  def generate(self, index: int):
    if (index < 0 or index >= len(self.seeds) - 1):
      return None

    seed1 = self.seeds[index]
    seed2 = self.seeds[index+1]
    prompt = GENERATOR_USER_PROMPT.format(
      task_1=seed1.description,
      setup_1=seed1.setup_command,
      success_1=seed1.success_condition,
      task_2=seed2.description,
      setup_2=seed2.setup_command,
      success_2=seed2.success_condition,
    )

    return self.client._generate(prompt)


class Solver:
  def __init__(self):
    pass

  def solve(task):
    pass


class Pipeline:
  def __init__(self):
    pass

  def run():
    pass


if __name__ == "__main__":
  seeds = []
  with open("../data/eval.jsonl", "r") as fhand:
    index = 0
    for line in fhand:
      if index >= 100:
        break

      seed = json.loads(line)
      seeds.append(
        Task(
          seed.get("difficulty_level"),
          seed.get("task"),
          " && ".join(seed.get("setup_commands")),
          seed.get("success_condition")
        )
      )
      index += 1

  generator = Generator(seeds)
  for i in range(1):
    print(seeds[i], seeds[i+1], sep='\n')
    print(generator.generate(i))
