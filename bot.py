import re
import asyncio
from openai import ChatCompletion

# Assuming the existence of a function logOutput similar to the JavaScript version
def logOutput(message):
    print(message)

async def handle_message(userText, chatId, chatType, Author, messagetime):
    botName = "nesimo"
    botFirstName = "nesimo"

    regex_botname = re.compile('@' + botName, re.IGNORECASE)
    regex_firstname = re.compile(botFirstName.lower(), re.IGNORECASE)
    logOutput("bot name: " + botName + " Name: " + botFirstName)
    logOutput(messagetime + " | ID: " + chatId + " | Type: " + chatType + " | Author: " + Author + " | Message: " + userText)

    # Check if the message is not empty and the bot is mentioned
    isGroup = chatType == "group" or chatType == "supergroup"
    shallReply = userText and ((chatType == "private" and userText) or
                               (isGroup and regex_botname.search(userText.strip())) or
                               (isGroup and regex_firstname.search(userText.strip().lower())))

    if shallReply:
        try:
            # Assuming the existence of a properly configured OpenAI client
            gpt_response = await ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Te llamas Tio Nesimo y eres un malandro del barrio de Caricuao en Caracas, Venezuela y hablas usando la tipica jerga de los malandros en caracas pero tambien eres un asistente útil."},
                    {"role": "user", "content": userText}
                ]
            )

            replyText = gpt_response.choices[0].message.content.strip()
            logOutput(messagetime + " | ID: " + chatId + " | Type" + chatType + " | Author: " + Author + " | Message: " + replyText)
        except Exception as e:
            logOutput(f"Error: {str(e)}")

# Example usage
# asyncio.run(handle_message("Hello there!", "12345", "private", "John Doe", "2023-04-01 12:00:00"))