import os
import logging
import json
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored  

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
OPENAI_ORG_ID = os.environ.get('OPENAI_ORG_ID')
OPENAI_PROJECT_ID = os.environ.get('OPENAI_PROJECT_ID')
OPENAI_PROJECT_SECRET_KEY = os.environ.get('OPENAI_PROJECT_SECRET_KEY')
ALLOW_USER_PASS= os.environ.get('ALLOW_USER_PASS')
ADMIN_PASS= os.environ.get('ADMIN_PASS')
GPT_MODEL = "gpt-4o"

client = OpenAI(organization=OPENAI_ORG_ID, project=OPENAI_PROJECT_ID, api_key=OPENAI_PROJECT_SECRET_KEY)

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "function": "magenta",
    }
    
    for message in messages:
        if message["role"] == "system":
            print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "user":
            print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and message.get("function_call"):
            print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "function":
            print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))


if __name__ == '__main__':
    # Determine the directory of the current script file
    script_dir = os.path.dirname(__file__)
    # Construct the path to the 'tools.json' file in the same directory
    tools_file_path = os.path.join(script_dir, 'tools.json')


    # Load the JSON file into a variable called tools
    with open(tools_file_path, 'r') as file:
        tools = json.load(file)
    
    messages = []
    messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
    # messages.append({"role": "user", "content": "I'm in Glasgow, Scotland."})
    # messages.append({"role": "user", "content": "What's the weather like today"})
    messages.append({"role": "user", "content": "what is the weather going to be like in Glasgow, Scotland over the next 5 days"})
 
    chat_response = chat_completion_request(
        messages, tools=tools
    )
    assistant_message = chat_response.choices[0].message
    messages.append(assistant_message)
    print(assistant_message)
    # pretty_print_conversation(messages)
