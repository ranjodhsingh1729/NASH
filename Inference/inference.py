import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class LLM:
  def __init__(self, model_name: str, device: str, system_prompt: str):
    self.model_name = model_name
    self.device = torch.device(device)
    self.system_prompt = system_prompt
    self.tokenizer = AutoTokenizer.from_pretrained(model_name)
    self.model = AutoModelForCausalLM.from_pretrained(
      model_name,
      torch_dtype=torch.float16,
    ).to(device)

    self.history = list()
    self.reset()

  def reset(self):
    self.history = [
      {
        "role": "system",
        "content": self.system_prompt
      },
    ]

  def generate(
    self,
    prompt: str,
    max_new_tokens: int = 100,
    temperature: int = 0.7,
    top_p = 0.9
  ):
    message = {"role": "user", "content": prompt}
    self.history.append(message)

    chat = self.tokenizer.apply_chat_template(
      self.history,
      tokenize=False,
      add_generation_prompt=True
    )
    request = self.tokenizer(chat, return_tensors="pt").to(self.device)
    with torch.no_grad():
      outputs = self.model.generate(
        **request,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p
      )
    response = self.tokenizer.decode(
        outputs[0][request.input_ids.shape[-1]:],
        skip_special_tokens=True
    )

    reply = {"role": "assistant", "content": response}
    self.histroy.append(reply)

    return reply["content"]
  

if __name__ == "__main__":
  model = LLM(
    "Qwen/Qwen2-1.5B-Instruct",
    "xpu",
    "You are a helpful assistant.",
  )

  while (True):
    prompt = input("Prompt: ")
    if prompt == "exit()":
      break
    print("Reponse: ", model.generate(prompt))
