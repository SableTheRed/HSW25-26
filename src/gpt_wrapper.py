from google import genai  # type: ignore[import-untyped]

class Wrapper:
    def __init__(self, system_prompt="You are emotionally supportive"):
        self.client = genai.Client()
        self.chat = self.client.chats.create(
            model="gemini-3-flash-preview",
            config={"system_instruction": system_prompt}
        )

    def send(self, user_message: str) -> str:
        response = self.chat.send_message(user_message)
        return response.text

bot = Wrapper()
while True:
    prompt = input("Enter a prompt or exit to speak to InsideOut: ")
    if prompt.lower() == "exit":
        break
    else:
        print(bot.send(prompt))