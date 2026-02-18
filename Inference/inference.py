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

    self.messages = list()
    self.reset()

  def reset(self, system_prompt: str = ""):
    self.messages = [
      {
        "role": "system",
        "content": system_prompt if system_prompt else self.system_prompt
      },
    ]

  def generate(
    self,
    prompt: str,
    max_new_tokens: int = 100,
    temperature: int = 0.7,
    top_p = 0.9
  ):
    self.messages.append({"role": "user", "content": prompt})

    text = self.tokenizer.apply_chat_template(
      self.messages,
      tokenize=False,
      add_generation_prompt=True
    )
    inputs = self.tokenizer(text, return_tensors="pt").to(self.device)

    with torch.no_grad():
      outputs = self.model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p
      )
    response = self.tokenizer.decode(
        outputs[0][inputs.input_ids.shape[-1]:],
        skip_special_tokens=True
    )

    self.messages.append({"role": "assistant", "content": response})
    return response
  

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
