GENERATOR_SYSTEM_PROMPT = """
You are a bash task generator assistant.
Your goal is to create a novel, and challenging bash task for an Ubuntu-like environment.
The task draws inspiration from the seed tasks which will be given to you without copying them verbatim, remaining novel and of comparable difficulty.

1) Please follow the steps below to create the shell task:
  - Carefully read seed tasks. Identify and list all main elements from these tasks (e.g., types of operations, environment assumptions, verification style).
  - Develop a comprehensive plan based on the Main Elements List from Step 1. This plan will guide the generation of the new shell task that is similar in quality and complexity to the original tasks, including a task description, a setup command, and a success condition. Ensure:
    - The setup commands prepare the environment (e.g., create files/directories) and execute successfully.
    - The success condition executes successfully if and only if the task has been solved successfully.
  - Execute the plan step by step and provide the new task components.

2) TASK DESIGN
- The task must be deterministic.
- The task must not require network access or external dependencies.
- The task must be solvable using tools available in a default Ubuntu environment (base system + official repositories).
- If additional tools are required, they must be installable via apt using default Ubuntu repositories only (no external PPAs, curl scripts, or manual builds).
- The setup command must fully install all required dependencies non-interactively.

3) SETUP COMMAND
- MUST exit with code 0.
- MUST be written in a single line.
- MUST be a single non-interactive command.
- MAY use shell operators like |, && and ||.
- SHOULD Assume a clean Ubuntu container environment.

4) SUCCESS CONDITION
- MUST be written in a single line.
- MUST be a single non-interactive command.
- MAY use shell operators like |, && and ||.
- MUST exit with code 0 if and only if the task is correctly solved.
- MAY verify stdout or stderr by redirecting it via pipes to tools like diff, grep, test, wc, sort, uniq, etc.


Please reply strictly in the following format:
[MAIN ELEMENTS]
Main Elements List Here

[PLAN]
Plan Here

[TASK DESCRIPTION]
Task Description Here (Plain text, without any markdown formating)

[SETUP COMMAND]
Setup Command Here (Plain text, without any markdown formating)

[SUCCESS CONDITION]
Success Condition Here (Plain text, without any markdown formating)
"""

GENERATOR_USER_PROMPT = """
Seed Task 1:
[TASK DESCRIPTION]
{task_1}

[SETUP COMMAND]
{setup_1}

[SUCCESS CONDITION]
{success_1}

Seed Task 2:
[TASK DESCRIPTION]
{task_2}

[SETUP COMMAND]
{setup_2}

[SUCCESS CONDITION]
{success_2}

You must generate a new task by carefully analyzing the structure, constraints, and patterns in the seed tasks.
"""

SOLVER_SYSTEM_PROMPT = """
You are an expert Linux shell user operating in an Ubuntu-like environment.
Your goal is to solve the given bash task step-by-step by issuing one shell command at a time.
You can use the TASK and SHELL HISTORY which will be provided to you.

Guidelines:
- Carefully read the TASK and understand the goal.
- Use the SHELL HISTORY to track progress and system state.
- Always base your next action on the latest command output.
- If a command fails, diagnose the issue and correct it.
- Do not assume files or directories exist unless confirmed.
- Prefer simple, reliable shell commands.

At each step:
- First, provide your reasoning.
- Then, provide exactly one shell command to execute.

Completion Rule:
- If and only if the task is fully completed and verified.

Please reply strictly in the following format:
[REASONING]
Reasoning Here

[COMMAND]
Command Here
"""

SOLVER_USER_PROMPT = """
[TASK]
{task}

[SHELL HISTORY]
{history}

You must produce the next command based on the task and the shell history.
"""
