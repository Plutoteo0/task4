import json
import anthropic
from dotenv import load_dotenv
from tools import TOOLS, run_tool

load_dotenv()
client = anthropic.Anthropic()
MODEL = "claude-haiku-5-5"

SYSTEM = (
    "You are an assistant for a bookstore analytics dashboard. "
    "There are five stores: STORE1..STORE5. "
    "Answer ONLY using results returned by the provided tools. "
    "Never guess, estimate or calculate numbers from memory: if a tool does not provide the data, "
    "say that you don't have it. If the user does not say which store, ask which one. "
    "Use the data_range from get_revenue to say when a requested period is outside the data. "
    "All money amounts are in USD. Answer in the language of the user's question, briefly."
    "report only facts present in tool results, plain text without markdown"
)

def answer(messages, metrics):
    for _ in range(6):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM,
            tools=TOOLS,
            messages=messages
        )

        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content)

        messages.append({"role": "assistant", "content": resp.content})

        results = []
        for block in resp.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input, metrics)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, ensure_ascii=False),
                })
        messages.append({"role": "user", "content": results})

    return "Sorry, I could not finish the request."

if __name__ == "__main__":
    from app import METRICS
    msgs = [{"role": "user", "content": "Кто лучший покупатель в STORE3"}]
    print(answer(msgs, METRICS))