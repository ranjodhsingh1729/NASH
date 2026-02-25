import json
from groq import Groq
from nash.env import GROQ_API_KEY
from typing import Dict, Any, Optional


class JSONClient:
    def __init__(
        self,
        model_name: str,
        system_prompt: str,
        json_schema: Dict[str, Any],
        top_p: float = 0.9,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ):
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.json_schema = json_schema
        self.top_p = top_p
        self.temperature = temperature
        self.max_tokens = max_tokens

        self.client = Groq(api_key=GROQ_API_KEY)
        self.history = []
        self.reset()

    def reset(self):
        self.history = [
            {"role": "system", "content": self.system_prompt}
        ]

    def _request(self, messages):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            temperature=self.temperature,
            response_format={
                "type": "json_schema",
                "json_schema": self.json_schema
            }
        )

        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    def generate_once(self, input_text: str) -> Dict[str, Any]:
        """
        One-shot structured generation (does not update history)
        """
        messages = self.history + [{"role": "user", "content": input_text}]

        return self._request(messages)

    def generate(self, input_text: str) -> Dict[str, Any]:
        """
        Conversational structured generation (updates history)
        """
        user_message = {"role": "user", "content": input_text}
        self.history.append(user_message)

        structured_output = self._request(self.history)

        assistant_message = {
            "role": "assistant",
            "content": json.dumps(structured_output)
        }

        self.history.append(assistant_message)

        return structured_output


if __name__ == "__main__":
    json_schema = {
        "name": "question_answer",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "answer": {"type": "string"}
            },
            "required": [
                "title",
                "answer"
            ],
            "additionalProperties": False
        }
    }

    client = JSONClient(
        model_name="openai/gpt-oss-120b",
        system_prompt="Answer the following questions.",
        json_schema=json_schema
    )

    while True:
        prompt = input("Prompt: ")
        if prompt == "exit()":
            break

        result = client.generate_once(prompt)
        print("Response:")
        print(json.dumps(result, indent=2))