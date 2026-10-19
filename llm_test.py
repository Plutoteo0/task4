from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()
resp = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=100,
    messages=[{"role": "user", "content": "Скажи одно слово: привет"}],
)
print(resp.content[0].text)