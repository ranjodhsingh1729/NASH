import os
from groq import Groq

class Client:
    def __init__(
        self,
        model,
        system_prompt,
        max_tokens = None,
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
        self.client = Groq(
            api_key = os.environ.get("GROQ_API_KEY")
        )

        self.history = list()

    def reset(self):
        self.history = [
            {"role": "system","content": self.system_prompt}
        ]

    def request(self, input):
        message = {"role": "user", "content": input}
        self.history.append(message)

        response = self.client.chat.completions.create(
            model = self.model,
            temperature = 0.7,
            messages = self.history,
            max_tokens = self.max_tokens
        )
        reply = {
            "role": "assistant",
            "content": response.choices[0].message.content
        }

        self.history.append(reply)
        return reply["content"]
    

if __name__ == "__main__":
    client = Client(
        "Qwen/Qwen3-32B",
        "You are a helpful assistant."
    )

    while (True):
        prompt = input("Prompt: ")
        if prompt == "exit()":
          break
        print("Reponse: ", client.request(prompt))
