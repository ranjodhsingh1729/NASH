from groq import Groq
from nash.env import GROQ_API_KEY


class CloudClient:
  def __init__(
    self,
    model_name: str,
    system_prompt: str,
    top_p: float = 0.9,
    temperature: float = 0.7,
    max_tokens: int = None,
  ):
    self.model_name = model_name
    self.system_prompt = system_prompt
    self.top_p = top_p
    self.temperature = temperature
    self.max_tokens = max_tokens

    self.client = Groq(api_key=GROQ_API_KEY)
    self.history = list()
    self.reset()

  def reset(self):
    self.history = [
      {"role": "system","content": self.system_prompt}
    ]

  def _request(self, messages):
    response = self.client.chat.completions.create(
      model = self.model_name,
      messages = messages,
      max_tokens = self.max_tokens,
      top_p = self.top_p,
      temperature = self.temperature,
    )

    return response.choices[0].message.content

  def generate_once(self, input):
    """
    One-shot generation (does not update history)
    """
    messages = self.history + [{"role": "user", "content": input}]
    
    return self._request(messages)

  def generate(self, input: str):
    """
    Conversational generation (updates history)
    """
    user_message = {"role": "user", "content": input}
    self.history.append(user_message)
    output = self._request(self.history)
    assistant_message = {"role": "assistant", "content": output}
    self.history.append(assistant_message)

    return output


if __name__ == "__main__":
    client = CloudClient(
      "openai/gpt-oss-120b",
      "You are a helpful assistant."
    )

    while (True):
      prompt = input("Prompt: ")
      if prompt == "exit()":
        break
      print("Reponse: ", client.generate_once(prompt))
