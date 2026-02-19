"""
Credits To:
https://arxiv.org/pdf/2507.23751
https://github.com/deathbyknowledge/sos
"""

from prompts import GENERATOR_PROMPT, SOLVER_PROMPT


class Task:
  setup_command: str
  solution_verification_command: str

class Solution:
  reasoning: str
  solution_command: str


class Generator:
  def __init__(self):
    self.prompt = GENERATOR_PROMPT

  def generate(seed):
    pass

class Solver:
  def __init__(self):
    self.prompt = SOLVER_PROMPT

  def solve(task):
    pass

class Pipeline:
  def __init__(self):
    pass

  def run():
    pass


if __name__ == "__main__":
  pass