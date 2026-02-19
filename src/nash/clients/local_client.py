import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class LocalClient:
  def __init__(
    self,
    model_name: str,
    device_name: str,
    system_prompt: str,
    top_p: float = 0.9,
    temperature: float = 0.7,
    max_tokens: int = 1000,
  ):
    self.model_name = model_name
    self.device_name = device_name
    self.system_prompt = system_prompt
    self.top_p = top_p
    self.temperature = temperature
    self.max_tokens = max_tokens

    self.device = torch.device(self.device_name)
    self.tokenizer = AutoTokenizer.from_pretrained(model_name)
    self.client = AutoModelForCausalLM.from_pretrained(
      model_name, dtype=torch.float16
    ).to(self.device)

    self.history = list()
    self.reset()

  def reset(self):
    self.history = [
      {"role": "system", "content": self.system_prompt},
    ]

  def generate(self, input: str):
    message = {"role": "user", "content": input}
    self.history.append(message)

    chat = self.tokenizer.apply_chat_template(
      self.history,
      tokenize=False,
      add_generation_prompt=True
    )
    request = self.tokenizer(chat, return_tensors="pt").to(self.device)
    with torch.no_grad():
      outputs = self.client.generate(
        **request,
        max_new_tokens=self.max_tokens,
        temperature=self.temperature,
        top_p=self.top_p
      )
    response = self.tokenizer.decode(
        outputs[0][request.input_ids.shape[-1]:],
        skip_special_tokens=True
    )

    reply = {"role": "assistant", "content": response}
    self.history.append(reply)
    return reply["content"]
  

if __name__ == "__main__":
  model = LocalClient(
    "Qwen/Qwen2.5-0.5B-Instruct",
    "xpu",
    "You are a helpful assistant.",
  )

  while (True):
    prompt = input("Prompt: ")
    if prompt == "exit()":
      break
    print("Reponse: ")
    print(model.generate(prompt))
