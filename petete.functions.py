import json
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored  



class Spirit:
    def __init__(self, model_name="gpt-4o", openAI_client=OpenAI()):
        self.GPT_MODEL = model_name
        self.client = openAI_client

    @retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(5))
    def generate_text(self, prompt):
        try:
            response = self.client.completions.create(
                model=self.model_name,
                prompt=prompt,
                max_tokens=50
            )
            return response.choices[0].text.strip()
        except Exception as e:
            print(colored(f"Error generating text: {e}", "red"))
            return None

    @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
    def chat_completion_request(self, messages, tools=None, tool_choice=None):
        try:
            response = self.client.chat.completions.create(
                model=self.GPT_MODEL,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
            )
            return response
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e

